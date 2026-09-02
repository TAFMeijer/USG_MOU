"""MoU dashboard — Investment area view.

The transpose of the Country investment view: pick one investment area and see the
whole portfolio through it — the global USG/government split for that area, every
country ranked by what it commits, and one small multiple per country ordered
largest to smallest. Panels use exactly the same stacked-area grammar as the country
view, so the two pages read the same way.
"""
import altair as alt
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(page_title="MoU dashboard — Investment area view", page_icon="🧭",
                   layout="wide")

# Same fix as the country view: the chart hover-toolbar is absolutely positioned
# above each chart and the fixed-height panel boxes would clip it.
st.markdown(
    """<style>
    div[data-testid="stElementToolbar"] { top: 0.35rem !important; right: 0.35rem !important; }
    .vega-embed summary { top: 2.4rem !important; right: 0.4rem !important; }
    </style>""",
    unsafe_allow_html=True,
)

YEAR_AXIS = alt.Axis(labelAngle=-45, labelFontSize=13, labelFontWeight="bold", title=None)


@st.cache_data
def data(include_imputed: bool, include_baseline: bool):
    df = lib.load_budget_series()
    if not include_imputed:
        df = df[df["Basis"] != lib.BASIS_IMPUTED]
    if not include_baseline:
        df = df[~df["Basis"].isin(lib.BASELINE_BASES)]
    return df.groupby(["Country", "Investment area", "Year", "Funder", "Basis"],
                      as_index=False)["Amount"].sum()


@st.cache_data
def countries_meta():
    return lib.load_countries().set_index("Country")


include_imputed = st.sidebar.toggle(
    "Include imputed govt $ (labs & HCW)", value=True,
    help="Government FTE commitments priced at government/USG unit rates where the "
         "MoU prints FTEs but no dollars. See Sources & methodology.",
)
include_baseline = st.sidebar.toggle(
    "Include pre-MoU / existing funding $", value=True,
    help="The existing government workforce the MoU tabulates, valued at reference "
         "rates, plus the printed existing commodity funding carried from 2026. "
         "Baseline effort, not MoU co-financing.",
)
show_ref = st.sidebar.toggle(
    "Show 2026-level reference", value=True,
    help=lib.md("Thin dotted line at the COMBINED 2026 level held flat in each panel — "
                "the de-facto pre-MoU baseline carried into year one. Read the stacked "
                "top edge against it: holding the line means government absorption keeps "
                "the area at its 2026 level. Reference only, never added to a total."),
)

df = data(include_imputed, include_baseline)
meta = countries_meta()
PAL = lib.palette()
FUNDERS = ["USG", lib.GOV_LABEL]
funder_scale = alt.Scale(domain=FUNDERS, range=[PAL["usg"], PAL["gov"]])

CATEGORY_AREAS = [a for a in lib.area_options(df) if a != "All areas combined"]
area = st.sidebar.selectbox("Investment area", CATEGORY_AREAS)

m = df[(df["Investment area"] == area) & (df["Funder"].isin(FUNDERS))]

# ---------------- header ----------------
st.markdown(f"## {area}")
ranked = (m.groupby("Country")["Amount"].sum().sort_values(ascending=False))
ranked = ranked[ranked > 0]
present = ranked.index.tolist()
all_countries = sorted(df["Country"].unique())
absent = [c for c in all_countries if c not in present]
years = sorted(m["Year"].unique())
st.caption(
    f"{len(present)} of the {len(all_countries)} published MoUs budget this area"
    + (f" · {years[0]}–{years[-1]}" if years else "")
    + " · panels below run largest to smallest · all source links on the "
    "[Sources & methodology](Sources_and_methodology) page"
)

usg_t = m.loc[m["Funder"] == "USG", "Amount"].sum()
gov_t = m.loc[m["Funder"] == lib.GOV_LABEL, "Amount"].sum()
comb_t = usg_t + gov_t
k1, k2, k3, k4 = st.columns(4)
k1.metric("USG, all countries", lib.fmt_usd(usg_t))
k2.metric("Government, all countries", lib.fmt_usd(gov_t))
k3.metric("Combined", lib.fmt_usd(comb_t))
k4.metric("USG share of combined", f"{100 * usg_t / comb_t:.0f}%" if comb_t else "–")

if len(present):
    top3 = ranked.head(3)
    st.caption(lib.md(
        f"Most concentrated in **{top3.index[0]}** ({lib.fmt_usd(top3.iloc[0])}, "
        f"{100 * top3.iloc[0] / comb_t:.0f}% of the area) — the top three "
        f"({', '.join(top3.index)}) carry {100 * top3.sum() / comb_t:.0f}% of everything "
        "committed to this area across all published MoUs."
    ))
if absent:
    st.caption(lib.md(
        "No dollar line for this area in: **" + ", ".join(absent) + "**. Either the MoU "
        "does not budget it, or it folds the spend into another category (several MoUs "
        "carry lab workers inside frontline healthcare workers, and four call strategic "
        "assistance 'technical assistance' instead)."
    ))

# ---------------- overview: ranked totals (left) + global trajectory (right) ----
st.markdown("#### The global picture for this area")
OVERVIEW_H = 520
ov1, ov2 = st.columns(2)

with ov1, st.container(border=True, height=OVERVIEW_H):
    # A ranked bar, not a donut: sixteen slices is unreadable, and reusing the
    # country hues here would put two countries on the same colour (the palette is
    # eight hues x two stroke styles, and an arc cannot carry a stroke style).
    # Bars are directly labelled, so identity needs no colour at all.
    tot = m.groupby(["Country", "Funder"], as_index=False)["Amount"].sum()
    tot = tot[tot["Country"].isin(present)]
    bars = (
        alt.Chart(tot)
        .mark_bar()
        .encode(
            y=alt.Y("Country:N", sort=present, title=None,
                    axis=alt.Axis(labelFontSize=12, labelOverlap=False)),
            x=alt.X("Amount:Q", title=None,
                    axis=alt.Axis(format="~s",
                                  labelExpr='replace(datum.label, "G", "bn")')),
            color=alt.Color("Funder:N", scale=funder_scale,
                            legend=alt.Legend(orient="bottom", title=None, labelLimit=0)),
            order=alt.Order("Funder:N", sort="ascending"),
            tooltip=["Country", "Funder", alt.Tooltip("Amount:Q", format=",.0f")],
        )
        .properties(height=max(300, 26 * len(present)),
                    title=alt.TitleParams("Full-term total by country", fontSize=13))
    )
    st.altair_chart(bars, use_container_width=True)
    st.caption("Ordered largest → smallest; the panel grid below follows the same order. "
               "Botswana's MoU runs 2026–28, so its bar covers three years, not five.")

with ov2, st.container(border=True, height=OVERVIEW_H):
    # The same stacked grammar as every panel below, summed across all countries —
    # so the global shape and each country's shape are read the same way.
    glob = m.groupby(["Funder", "Year"], as_index=False)["Amount"].sum()
    glob["ord"] = (glob["Funder"] != "USG").astype(int)
    g26 = m.loc[m["Year"] == 2026, "Amount"].sum()
    gch = (
        alt.Chart(glob)
        .mark_area(line=True, opacity=0.75)
        .encode(
            x=alt.X("Year:O", axis=YEAR_AXIS),
            y=alt.Y("Amount:Q", stack="zero", title=None,
                    axis=alt.Axis(format="~s",
                                  labelExpr='replace(datum.label, "G", "bn")')),
            color=alt.Color("Funder:N", scale=funder_scale, legend=None),
            order=alt.Order("ord:Q"),
            tooltip=["Funder", "Year", alt.Tooltip("Amount:Q", format=",.0f")],
        )
        .properties(height=max(300, 26 * len(present)) - 20,
                    title=alt.TitleParams("All countries combined, per year", fontSize=13))
    )
    if g26 > 0:
        glab = glob.sort_values(["Year", "ord"]).copy()
        glab["share"] = glab["Amount"] / g26
        glab["cum"] = glab.groupby("Year")["Amount"].cumsum()
        glab["mid"] = glab["cum"] - glab["Amount"] / 2
        glab = glab[glab["share"] >= 0.05]
        if len(glab):
            gch = gch + (
                alt.Chart(glab)
                .mark_text(fontSize=10, fontWeight="bold", color="white")
                .encode(x=alt.X("Year:O", axis=YEAR_AXIS), y="mid:Q",
                        text=alt.Text("share:Q", format=".0%"),
                        tooltip=["Funder", "Year",
                                 alt.Tooltip("share:Q", format=".1%",
                                             title="Share of the 2026 combined level"),
                                 alt.Tooltip("Amount:Q", format=",.0f")])
            )
        if show_ref:
            gref = pd.DataFrame({"Year": years, "Amount": g26})
            gch = gch + (
                alt.Chart(gref)
                .mark_line(strokeDash=[2, 2], strokeWidth=1.4, color=PAL["muted"],
                           opacity=0.9)
                .encode(x=alt.X("Year:O", axis=YEAR_AXIS), y="Amount:Q",
                        tooltip=[alt.Tooltip("Amount:Q", format=",.0f",
                                             title="2026 combined level (reference)")])
            )
    st.altair_chart(gch, use_container_width=True)
    st.caption(lib.md(
        "USG at the bottom, government stacked on top — the top edge is combined "
        "funding for this area across every published MoU. Percentages are each band "
        "against the 2026 combined level, so the two together read as 'this year vs 2026'."
    ))

# printed MoU footnotes attached to this area, whichever country prints them
area_fns = lib.budget_footnotes(area=area, funders=FUNDERS)
if area_fns:
    st.markdown(lib.footnote_block(area_fns), unsafe_allow_html=True)

# ---------------- small multiples, largest -> smallest ----------------
st.markdown(f"#### {area} by country, largest to smallest (US$ per year)")

PANEL_H = 315   # box height, identical for every panel
CHART_H = 235   # chart inside the box, leaving room for a printed footnote


def render_country_panel(cty: str) -> None:
    sub = lib.attach_budget_notes(m[m["Country"] == cty], area)
    panel_fns = lib.budget_footnotes(area=area, country=cty, funders=FUNDERS)
    sub_f = sub.groupby(["Funder", "Year"], as_index=False)["Amount"].sum()
    sub_f["ord"] = (sub_f["Funder"] != "USG").astype(int)  # USG at the bottom
    total = sub_f["Amount"].sum()
    yrs = sorted(sub["Year"].unique())
    subtitle = (f"{lib.fmt_usd(total)} · {100 * total / comb_t:.1f}% of the area"
                + (f" · {yrs[0]}–{yrs[-1]}" if yrs else ""))
    ch = (
        alt.Chart(sub_f)
        .mark_area(line=True, opacity=0.75)
        .encode(
            x=alt.X("Year:O", axis=YEAR_AXIS),
            y=alt.Y("Amount:Q", stack="zero", title=None,
                    axis=alt.Axis(format="~s",
                                  labelExpr='replace(datum.label, "G", "bn")')),
            color=alt.Color("Funder:N", scale=funder_scale, legend=None),
            order=alt.Order("ord:Q"),
            tooltip=["Funder", "Year", alt.Tooltip("Amount:Q", format=",.0f")]
                    + ([alt.Tooltip("MoU footnote:N")] if panel_fns else []),
        )
        .properties(height=CHART_H,
                    title=alt.TitleParams(cty, fontSize=13, subtitle=subtitle,
                                          subtitleFontSize=10,
                                          subtitleColor=PAL["muted"]))
    )
    c26 = sub.loc[sub["Year"] == 2026, "Amount"].sum()
    if c26 > 0:
        lab = sub_f.sort_values(["Year", "ord"]).copy()
        lab["share"] = lab["Amount"] / c26
        lab["cum"] = lab.groupby("Year")["Amount"].cumsum()
        lab["mid"] = lab["cum"] - lab["Amount"] / 2
        lab = lab[lab["share"] >= 0.05]
        if len(lab):
            ch = ch + (
                alt.Chart(lab)
                .mark_text(fontSize=10, fontWeight="bold", color="white")
                .encode(x=alt.X("Year:O", axis=YEAR_AXIS), y="mid:Q",
                        text=alt.Text("share:Q", format=".0%"),
                        tooltip=["Funder", "Year",
                                 alt.Tooltip("share:Q", format=".1%",
                                             title="Share of the 2026 combined level"),
                                 alt.Tooltip("Amount:Q", format=",.0f")])
            )
        if show_ref:
            ref = pd.DataFrame({"Year": yrs, "Amount": c26})
            ch = ch + (
                alt.Chart(ref)
                .mark_line(strokeDash=[2, 2], strokeWidth=1.4, color=PAL["muted"],
                           opacity=0.9)
                .encode(x=alt.X("Year:O", axis=YEAR_AXIS), y="Amount:Q",
                        tooltip=[alt.Tooltip("Amount:Q", format=",.0f",
                                             title="2026 combined level (reference)")])
            )
    st.altair_chart(ch, use_container_width=True)
    if panel_fns:
        st.markdown(lib.footnote_block(panel_fns, size_px=10), unsafe_allow_html=True)


for start in range(0, len(present), 3):
    row_cols = st.columns(3)
    for j, cty in enumerate(present[start:start + 3]):
        with row_cols[j], st.container(border=True, height=PANEL_H):
            render_country_panel(cty)

st.markdown(
    f'<span style="color:{PAL["usg"]};font-weight:600">▮ USG (bottom)</span> &nbsp; '
    f'<span style="color:{PAL["gov"]};font-weight:600">▮ Govt, stacked on top — '
    'top edge = combined funding</span> &nbsp; '
    f'<span style="color:{PAL["muted"]}">·· 2026 combined level (reference)</span> '
    '<span style="color:white;font-weight:700">%</span> '
    f'<span style="color:{PAL["muted"]};font-size:12px">= share of that country\'s '
    "2026 combined level for this area (>100% = growth, <100% = shortfall; labels "
    'under 5% hidden). Panels share a grammar, not a y-axis — each is scaled to its '
    'own country, so compare shapes here and levels in the ranked bar above.</span>',
    unsafe_allow_html=True,
)

# ---------------- detail table ----------------
with st.expander(f"Line-item detail for {area} (as printed in the MoUs, with caveats)"):
    detail = lib.load_budget_tidy()
    detail = detail[detail["Investment area"] == area]
    f1, f2, f3 = st.columns([2, 1.6, 2])
    with f1:
        f_country = st.multiselect("Country", sorted(detail["Country"].unique()),
                                   key="ia_country")
    with f2:
        f_funder = st.multiselect("Funder", sorted(detail["Funder"].unique()),
                                  key="ia_funder")
    with f3:
        f_row = st.multiselect("Row type", sorted(detail["Row type"].unique()),
                               key="ia_rowtype")
    if f_country:
        detail = detail[detail["Country"].isin(f_country)]
    if f_funder:
        detail = detail[detail["Funder"].isin(f_funder)]
    if f_row:
        detail = detail[detail["Row type"].isin(f_row)]
    st.dataframe(detail, use_container_width=True, hide_index=True,
                 column_config={"Amount": st.column_config.NumberColumn(
                     "Amount", format="localized")})
    st.caption(lib.md(
        f"{len(detail):,} rows. To sum money safely: filter Unit = USD and Row type = "
        "'Line item' (plus the existing-government rows) — the MoUs' own subtotals and "
        "appendix breakdowns are flagged so they don't double-count."
    ))
