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
m = m.sort_values("Year")

k1, k2, k3 = st.columns(3)
k1.metric("Indicators in this MoU", m["Indicator"].nunique())
k2.metric("Outcome metrics", m.loc[m["Metric type"] == "Outcome", "Indicator"].nunique())
k3.metric("Process metrics", m.loc[m["Metric type"] == "Process", "Indicator"].nunique())

SECTION_ORDER = ["Outcome", "Process", "Outbreak response (7-1-7)", "Co-investment benchmark"]
SECTION_BLURB = {
    "Outcome": "Health outcomes the agreement commits to improving.",
    "Process": "Service-delivery volumes and coverage rates that are audited annually.",
    "Outbreak response (7-1-7)": "Detect within 7 days, notify within 1 day, respond within "
    "7 days. Most MoUs state these as standing commitments; Nigeria also sets baselines "
    "and 5-year targets.",
    "Co-investment benchmark": "Domestic financing benchmarks tied to continued USG funding.",
}


def indicator_chart(sub: pd.DataFrame, is_pct: bool) -> alt.Chart:
    label = sub["Indicator"].iat[0]
    short = label if len(label) <= 55 else label[:52] + "…"
    y = alt.Y(
        "Value:Q",
        title=None,
        scale=alt.Scale(domain=[0, 100]) if is_pct else alt.Scale(zero=False),
        axis=alt.Axis(format="d") if is_pct else alt.Axis(format="~s"),
    )
    return (
        alt.Chart(sub)
        .mark_line(point=True, strokeWidth=2.5, color=lib.USG_COLOR)
        .encode(
            x=alt.X("Year:O", sort=YEAR_ORDER, axis=YEAR_AXIS),
            y=y,
            tooltip=["Indicator", "Year", "Value", "Unit", "Unit / source note"],
        )
        .properties(height=170, title=alt.TitleParams(short, fontSize=12))
    )


for section in SECTION_ORDER:
    sec = m[m["Metric type"] == section]
    if sec.empty:
        continue
    st.markdown(f"#### {section} metrics")
    st.caption(SECTION_BLURB.get(section, ""))
    indicators = list(dict.fromkeys(sec["Indicator"]))  # preserve MoU order
    cols = st.columns(3)
    for i, ind in enumerate(indicators):
        sub = sec[sec["Indicator"] == ind].dropna(subset=["Value"])
        if sub.empty:
            continue
        is_pct = (sub["Value type"] == "Percentage").all()
        with cols[i % 3]:
            unit_lbl = sub["Unit"].iat[0]
            st.altair_chart(indicator_chart(sub, is_pct), use_container_width=True)
            st.caption(f"Unit: {unit_lbl}")

# ---------------- detail table ----------------
with st.expander("Data table & download"):
    st.dataframe(
        m,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Source (MoU PDF)": st.column_config.LinkColumn("Source (MoU PDF)",
                                                            display_text="open PDF")
        },
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
