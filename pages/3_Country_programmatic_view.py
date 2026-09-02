"""MoU dashboard — Country programmatic view (v0).

One country at a time: every Section-1 indicator as its own small chart, grouped
by metric type, so mixed units never share an axis. Ideas for v1 at the bottom.
"""
import altair as alt
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(page_title="MoU dashboard — Country programmatic view", page_icon="📈",
                   layout="wide")

YEAR_ORDER = ["Baseline", "2026", "2027", "2028", "2029", "2030"]
YEAR_AXIS = alt.Axis(labelAngle=-45, labelFontSize=12, labelFontWeight="bold", title=None)


@st.cache_data
def data():
    return lib.load_programmatic()


@st.cache_data
def countries_meta():
    return lib.load_countries().set_index("Country")


p = data()
meta = countries_meta()
PAL = lib.palette()  # follows the active (system-preference) theme

country = st.sidebar.selectbox("Country", sorted(p["Country"].unique()))
pareas = st.sidebar.multiselect(
    "Programmatic area",
    sorted(p.loc[p["Country"] == country, "Programmatic area"].unique()),
    default=sorted(p.loc[p["Country"] == country, "Programmatic area"].unique()),
)

# ---------------- header with source link ----------------
row = meta.loc[country]
url = row.get("MoU PDF URL", "")
host = row.get("Hosted by", "")
title = f"[{country}]({url})" if isinstance(url, str) and url.startswith("http") else country
st.markdown(f"## {title} — programmatic targets")
st.caption(
    f"Signed {row['Signed']} · baselines and 2026–2030 targets as printed in Section 1 of "
    f"the MoU"
    + (f" (hosted by {host}; click the country name to open the PDF)" if host else "")
    + " · all source links on the [Sources & methodology](Sources_and_methodology) page. "
    "Values are as printed; some targets are inequalities ('>95%', '<140') — see each "
    "chart's tooltip."
)

m = p[(p["Country"] == country) & (p["Programmatic area"].isin(pareas))].copy()
m["Year"] = pd.Categorical(m["Year"], categories=YEAR_ORDER, ordered=True)
m = m.sort_values("Year", kind="stable")  # stable: keeps the MoU's own row order within a year

k1, k2, k3 = st.columns(3)
k1.metric("Indicators in this MoU", m["Indicator"].nunique())
k2.metric("Outcome metrics", m.loc[m["Metric type"] == "Outcome", "Indicator"].nunique())
k3.metric("Process metrics", m.loc[m["Metric type"] == "Process", "Indicator"].nunique())

# ---------------- footnotes printed in the MoU's own tables ----------------
fn_rows = m[m[lib.FOOTNOTE_COL] != ""]
if not fn_rows.empty:
    fn_groups = (
        fn_rows.groupby([lib.FOOTNOTE_COL, lib.FOOTNOTE_LOC_COL], sort=False)["Indicator"]
        .apply(lambda s: sorted(set(s)))
        .reset_index()
    )
    with st.expander(
        f"Footnotes printed in this MoU's indicator tables "
        f"({len(fn_groups)}) — charts carrying one are marked *",
        expanded=False,
    ):
        st.caption(
            "Transcribed verbatim. Each note travels with every year of the "
            "indicator(s) it qualifies; the location shows exactly which cells "
            "carry the printed marker."
        )
        for _, r in fn_groups.iterrows():
            inds = r["Indicator"]
            cover = ", ".join(inds[:4]) + (f" … +{len(inds) - 4} more" if len(inds) > 4 else "")
            st.markdown(
                f"* “{r[lib.FOOTNOTE_COL]}” — *{r[lib.FOOTNOTE_LOC_COL]}* · "
                f"applies to: {cover}"
            )

# Domestic-financing benchmarks are NOT a section here: they are money
# commitments, carried on the budget side (strategic_areas.csv and the pledge
# rows of budget_tidy.csv), and repeating them as "indicators" invites
# double-reading. A Metric type absent from this list simply will not render —
# analysis/validate_data.py checks that none is.
SECTION_ORDER = ["Outcome", "Process", "Outbreak response (7-1-7)"]
SECTION_BLURB = {
    "Outcome": "Health outcomes the agreement commits to improving.",
    "Process": "Service-delivery volumes and coverage rates that are audited annually.",
    "Outbreak response (7-1-7)": "Detect within 7 days, notify within 1 day, respond within "
    "7 days. Most MoUs state these as standing commitments; Nigeria also sets baselines "
    "and 5-year targets.",
}


def indicator_chart(sub: pd.DataFrame, is_pct: bool, is_717: bool = False) -> alt.Chart:
    label = sub["Indicator"].iat[0]
    short = label if len(label) <= 55 else label[:52] + "…"
    has_note = bool((sub[lib.FOOTNOTE_COL] != "").any())
    if has_note:
        short += " *"  # a footnote printed in the MoU applies to this indicator
    if is_717:
        # 7-1-7 commitments: fixed 0-10 day axis so the 7 / 1 / 7 pattern reads instantly
        y = alt.Y("Value:Q", title=None,
                  scale=alt.Scale(domain=[0, 10]),
                  axis=alt.Axis(values=[0, 1, 7, 10], format="d"))
    elif is_pct:
        y = alt.Y("Value:Q", title=None, scale=alt.Scale(domain=[0, 100]),
                  axis=alt.Axis(format="d"))
    elif lib.lower_is_better(sub):
        # Deaths / mortality / new cases: anchor at zero so the size of the
        # promised reduction is read in true proportion.
        top = float(sub["Value"].max())
        y = alt.Y("Value:Q", title=None,
                  scale=alt.Scale(domain=[0, top * 1.08 if top > 0 else 1]),
                  axis=alt.Axis(format="~s"))
    else:
        y = alt.Y("Value:Q", title=None, scale=alt.Scale(zero=False),
                  axis=alt.Axis(format="~s"))
    # Tall plotting area so small target movements (e.g. 91% -> 95% on the fixed
    # 0-100 scale) stay visible; the flat 7-1-7 day commitments don't need it.
    height = 180 if is_717 else 340
    return (
        alt.Chart(sub)
        .mark_line(point=True, strokeWidth=2.5, color=PAL["usg"])
        .encode(
            x=alt.X("Year:O", sort=YEAR_ORDER, axis=YEAR_AXIS),
            y=y,
            tooltip=["Indicator", "Year", "Value", "Unit", "Unit / source note"]
            + ([alt.Tooltip(f"{lib.FOOTNOTE_COL}:N", title="MoU footnote")]
               if has_note else []),
        )
        .properties(height=height, title=alt.TitleParams(short, fontSize=12))
    )


def order_717(indicators):
    """Detect -> notify -> respond, regardless of print order in the MoU.

    Keyed on the timeframe/verb rather than bare substrings: 'Notify USG within
    1 day of detection' contains the word 'detection', so matching on 'detect'
    alone mis-files the notify step.
    """
    def key(name):
        t = name.lower()
        if "full 7-1-7" in t:            # Nigeria's overall achievement metric: last
            return 3
        if "1 day" in t or "one day" in t:
            return 1                     # the notify step is the only 1-day commitment
        if any(k in t for k in ("complet", "respond", "response", "implement")):
            return 2
        if "detect" in t:
            return 0
        return 4
    return sorted(indicators, key=key)


for section in SECTION_ORDER:
    sec = m[m["Metric type"] == section]
    if sec.empty:
        continue
    st.markdown(f"#### {section} metrics")
    st.caption(SECTION_BLURB.get(section, ""))
    indicators = list(dict.fromkeys(sec["Indicator"]))  # preserve MoU order
    if section == "Outbreak response (7-1-7)":
        indicators = order_717(indicators)
    cols = st.columns(3)
    for i, ind in enumerate(indicators):
        sub = sec[sec["Indicator"] == ind].dropna(subset=["Value"])
        if sub.empty:
            continue
        is_pct = (sub["Value type"] == "Percentage").all()
        # Only DAY-denominated 7-1-7 commitments get the 0-10 day axis. Other
        # day-unit indicators (e.g. procurement lead time, 201 days) must not be
        # squeezed onto it, and neither must the countries that state 7-1-7 as
        # percentages of events met (Nigeria) — those belong on the 0-100 axis,
        # so the test is per indicator, not per section.
        is_717 = section == "Outbreak response (7-1-7)" and not is_pct
        with cols[i % 3]:
            unit_lbl = sub["Unit"].iat[0]
            st.altair_chart(indicator_chart(sub, is_pct, is_717), use_container_width=True)
            if not is_717 and not is_pct and lib.lower_is_better(sub):
                st.caption(f"Unit: {unit_lbl} · ▼ lower is better (axis from 0)")
            else:
                st.caption(f"Unit: {unit_lbl}")

# ---------------- detail table ----------------
with st.expander("Data table & download"):
    tbl = m.copy()
    f1, f2, f3 = st.columns([1.6, 1.6, 2.5])
    with f1:
        f_mtype = st.multiselect("Metric type", sorted(tbl["Metric type"].unique()),
                                 placeholder="All types")
    with f2:
        f_vtype = st.multiselect("Value type", sorted(tbl["Value type"].unique()),
                                 placeholder="All value types")
    with f3:
        f_text = st.text_input("Search indicator", "", placeholder="e.g. ART, measles, ANC…")
    if f_mtype:
        tbl = tbl[tbl["Metric type"].isin(f_mtype)]
    if f_vtype:
        tbl = tbl[tbl["Value type"].isin(f_vtype)]
    if f_text:
        tbl = tbl[tbl["Indicator"].str.contains(f_text, case=False, na=False)]
    st.dataframe(
        tbl,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Value": st.column_config.NumberColumn(format="localized"),
            "Source (MoU PDF)": st.column_config.LinkColumn("Source (MoU PDF)",
                                                            display_text="open PDF"),
        },
    )
    st.caption(
        f"{len(tbl):,} rows shown. Click any column header to sort; the 🔍 icon in the "
        "table toolbar does a live full-text search. 'MoU footnote (verbatim)' holds the "
        "notes the MoU itself prints on its indicator tables, carried across every year "
        "of the affected indicator."
    )
    st.download_button(
        "Download full tidy programmatic table (CSV)",
        (lib.DATA / "programmatic_tidy.csv").read_bytes(),
        file_name="programmatic_tidy.csv",
        mime="text/csv",
    )

st.markdown(
    """
---
##### Ideas for v1 (open for discussion)
- **Cross-country comparison for the common indicators** — the ~12 indicators that appear
  in nearly every MoU (ART, viral suppression, TB notification, ITNs, ANC4+, measles
  vaccine, data-audit accuracy…) as one comparable page.
- **Ambition index**: % change from baseline to 2030 per indicator (needs care with mixed
  units and inequality-coded targets).
- **Link targets to money**: overlay each indicator with the matching investment-area
  budget from the Country investment view.
- **Progress tracking**: once countries begin reporting, add actuals against these targets.
"""
)
