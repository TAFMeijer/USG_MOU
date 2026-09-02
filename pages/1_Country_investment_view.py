"""MoU dashboard — Country investment view (small multiples per investment area)."""
import altair as alt
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(page_title="MoU dashboard — Country investment view", page_icon="💵",
                   layout="wide")

# The chart hover-toolbar (fullscreen / download PNG / Vega "..." menu) is
# absolutely positioned ABOVE each chart; the bordered fixed-height panel
# boxes clip it. Pull it inside the box: it now overlays the chart's top-right
# corner, still only on hover, so the box aesthetic is unchanged.
st.markdown(
    """<style>
    div[data-testid="stElementToolbar"] {
        top: 0.35rem !important;
        right: 0.35rem !important;
    }
    .vega-embed summary {
        top: 2.4rem !important;
        right: 0.4rem !important;
    }
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
    # Per-area gov series are single-basis per (imputed/baseline are separate
    # series), so keeping Basis in the grain draws them as distinct lines;
    # "All areas combined" (KPIs only) may carry several rows per year, which
    # .sum() handles.
    df = df.groupby(["Country", "Investment area", "Year", "Funder", "Basis"],
                    as_index=False)["Amount"].sum()
    return lib.add_share(df)


@st.cache_data
def countries_meta():
    return lib.load_countries().set_index("Country")


include_imputed = st.sidebar.toggle(
    "Include imputed govt $ (labs & HCW)", value=True,
    help="Government FTE commitments priced at government/USG unit rates where the "
         "MoU prints FTEs but no dollars (Cameroon, Ethiopia labs, Mozambique labs, "
         "Rwanda, Côte d'Ivoire) — or, for Uganda, prices only each year's new cohort "
         "(the continuation of absorbed cohorts is imputed). Workers absorbed in year "
         "t stay funded in every later year. Summed into the government band of each "
         "panel; switch off to see printed $ only. See Sources & methodology.",
)
include_baseline = st.sidebar.toggle(
    "Include pre-MoU / existing funding $", value=True,
    help="Two pre-MoU components: the existing government workforce the MoU "
         "tabulates, valued at reference rates (CIV, Uganda, Mozambique, Liberia), "
         "and the government funding the MoUs mark as existing rather than new "
         "(Kenya, Uganda, CIV, Liberia, Mozambique, Cameroon). Baseline effort, not "
         "MoU co-financing; switching off lowers the government band accordingly.",
)
show_usg_ref = st.sidebar.toggle(
    "Show 2026-level reference", value=True,
    help=lib.md("Thin dotted line at the COMBINED 2026 level (USG + government "
                "where the government already funds in 2026) held flat in each "
                "panel — the de-facto pre-MoU baseline carried into year one "
                "(Rwanda's MoU states 2026 = what the USG 'currently funds'). "
                "Read the stacked top edge against it: holding the line means "
                "government absorption keeps the area at its 2026 level. "
                "Reference only — never added to any total."),
)
df = data(include_imputed, include_baseline)
meta = countries_meta()
PAL = lib.palette()  # follows the active (system-preference) theme

country = st.sidebar.selectbox("Country", sorted(df["Country"].unique()))
# The stacked panels carry everything the old Unit / Funder selectors switched
# between: both funders are always shown (USG bottom, government on top) and
# yearly shares appear as in-band labels — so the selectors are gone.
unit = "US$"
panel_style = "Stacked area"
funders = ["USG", lib.GOV_LABEL]

# ---------------- header with source link ----------------
row = meta.loc[country]
url = row.get("MoU PDF URL", "")
host = row.get("Hosted by", "")
title = f"[{country}]({url})" if isinstance(url, str) and url.startswith("http") else country
st.markdown(f"## {title}")
st.caption(
    f"Signed {row['Signed']} · {row['Doc type']} · "
    + (f"full text hosted by {host} (click the country name to open the PDF) · " if host else "")
    + "all source links on the [Sources & methodology](Sources_and_methodology) page"
)

# KPIs computed from the same summable line items the charts use, so the headline
# numbers and the charts below always agree.
cc = df[(df["Country"] == country) & (df["Investment area"] == "All areas combined")]
# Term length is read from the data, not assumed: Botswana's MOU runs 2026-2028 while
# every other published text runs 2026-2030, so the labels must follow the country.
_yrs = sorted(df.loc[df["Country"] == country, "Year"].unique())
TERM = f"{_yrs[0]}\u2013{_yrs[-1]}" if _yrs else "2026\u20132030"
usg_t = cc.loc[cc["Funder"] == "USG", "Amount"].sum()
gov_t = cc.loc[cc["Funder"] == lib.GOV_LABEL, "Amount"].sum()
comb_t = usg_t + gov_t
k1, k2, k3, k4 = st.columns(4)
k1.metric(f"USG, {TERM}", lib.fmt_usd(usg_t))
k2.metric("Govt co-financing (new + existing)", lib.fmt_usd(gov_t))
k3.metric("Combined (itemised)", lib.fmt_usd(comb_t))
k4.metric("USG share of combined", f"{100 * usg_t / comb_t:.0f}%" if comb_t else "–")

# flag the imputed / baseline components of the headline government figure
imp_t = lib.imputed_total(df, country)
base_t = (lib.imputed_total(df, country, lib.BASIS_BASELINE)
          + lib.imputed_total(df, country, lib.BASIS_PRINTED_EXISTING))
if include_imputed and imp_t > 0:
    st.caption(lib.md(
        f"⚠️ The government figures include **{lib.fmt_usd(imp_t)} of imputed $** "
        "for frontline labs & healthcare workers — " + lib.IMPUTED_CAPTION
    ))
if include_baseline and base_t > 0:
    st.caption(lib.md(
        f"⚠️ They also include **{lib.fmt_usd(base_t)} of pre-MoU / existing "
        "funding $** — " + lib.BASELINE_CAPTION
    ))
if show_usg_ref:
    if panel_style == "Stacked area":
        _c26 = cc.loc[cc["Year"] == 2026, "Amount"].sum()
        if _c26 > 0 and comb_t > 0:
            _ref5 = 5 * _c26
            _delta = comb_t - _ref5
            _word = "above" if _delta >= 0 else "below"
            st.caption(lib.md(
                f"Reference: the dotted line marks the **2026 combined level** "
                f"(USG + government, {lib.fmt_usd(_c26)}/yr) held flat — "
                f"{lib.fmt_usd(_ref5)} over the term vs {lib.fmt_usd(comb_t)} "
                f"planned combined, i.e. **{lib.fmt_usd(abs(_delta))} {_word}** "
                "the 2026 level. Where a panel's top edge holds the dotted line, "
                "government absorption keeps that area at its 2026 level."
            ))

# printed MoU footnotes that qualify this country's headline totals
hfns = lib.budget_footnotes(area="All areas combined", country=country)
if hfns:
    st.markdown(lib.footnote_block(hfns), unsafe_allow_html=True)

share = row["USG share"]
st.caption(lib.md(
    f"For reference, the **KFF headline** for {country} is "
    f"{lib.fmt_usd(row['Total agreement (USD)'])} total — "
    f"{lib.fmt_usd(row['USG (USD)'])} USG / "
    f"{lib.fmt_usd(row['Co-financing (USD)'])} co-financing"
    + (f" ({100 * share:.0f}% USG)" if pd.notna(share) else "")
    + ". KFF counts each MoU's headline pledge, which for some countries is a "
    "domestic-expenditure-increase commitment rather than itemised funding, so it can "
    "differ from the itemised amounts charted on this page — see Sources & methodology."
))

# ---------------- data for this country ----------------
m = df[
    (df["Country"] == country)
    & (df["Funder"].isin(funders))
    & (df["Investment area"] != "All areas combined")
]

# ---------------- overview row: donut (left) + area trajectories (right) -----
st.markdown(f"#### How the investment areas compare, {TERM}")

donut_src = (
    m.groupby("Investment area")["Amount"].sum().reset_index().query("Amount > 0")
    .sort_values("Amount", ascending=False)
)
donut_total = donut_src["Amount"].sum()
donut_src["Share of total"] = donut_src["Amount"] / donut_total

# Domain in size order -> legend reads large-to-small, matching the clockwise
# arcs; colors stay fixed per area (looked up, not positional). The SAME scale
# colors the trajectory chart on the right, so one legend serves both.
ordered_areas = donut_src["Investment area"].tolist()
area_scale = alt.Scale(
    domain=ordered_areas, range=[PAL["area"][a] for a in ordered_areas]
)
donut_sel = alt.selection_point(fields=["Investment area"], bind="legend",
                                name="area_sel")

# Two boxes, cross-highlighted: the donut (left box) carries the single legend
# on its right edge — visually between the two boxes. Clicking a legend entry
# or arc triggers a Streamlit selection rerun (on_select), and the trajectory
# chart (right box) highlights the same area. Both charts stay responsive.
OVERVIEW_H = 430
ov1, ov2 = st.columns(2)
with ov1, st.container(border=True, height=OVERVIEW_H):
    arcs = (
        alt.Chart(donut_src)
        .mark_arc(innerRadius=72, stroke=PAL["surface"], strokeWidth=2)
        .encode(
            theta=alt.Theta("Amount:Q"),
            color=alt.Color(
                "Investment area:N",
                scale=area_scale,
                legend=alt.Legend(labelLimit=0, title=None, orient="right",
                                  labelFontSize=12, symbolSize=110, symbolLimit=0),
            ),
            order=alt.Order("Amount:Q", sort="descending"),
            opacity=alt.condition(donut_sel, alt.value(1), alt.value(0.25)),
            tooltip=[
                "Investment area",
                alt.Tooltip("Amount:Q", format=",.0f", title=f"US$ {TERM}"),
                alt.Tooltip("Share of total:Q", format=".1%"),
            ],
        )
        .add_params(donut_sel)
    )
    center_value = (
        alt.Chart(pd.DataFrame({"label": [lib.fmt_usd(donut_total)]}))
        .mark_text(fontSize=22, fontWeight="bold", color=PAL["ink"], dy=-6)
        .encode(text="label:N")
    )
    center_sub = (
        alt.Chart(pd.DataFrame({"label": [TERM]}))
        .mark_text(fontSize=11, color=PAL["muted"], dy=13)
        .encode(text="label:N")
    )
    ev = st.altair_chart(
        (arcs + center_value + center_sub).properties(
            height=320, title=alt.TitleParams(f"Totals by area, {TERM}", fontSize=13)),
        use_container_width=True,
        on_select="rerun", key=f"area_donut_{country}",
    )
    st.caption("Legend ordered large → small — click an entry (or an arc) to "
               "highlight that area here AND in the trajectory chart; click "
               "again to reset.")

# areas selected in the donut (empty tuple/list = nothing selected)
_sel = []
try:
    _sel = [d["Investment area"] for d in ev["selection"]["area_sel"]
            if "Investment area" in d]
except Exception:  # fall back: scan whatever params the event carries
    try:
        for _v in ev["selection"].values():
            _sel += [d["Investment area"] for d in _v if isinstance(d, dict)
                     and "Investment area" in d]
    except Exception:
        pass

with ov2, st.container(border=True, height=OVERVIEW_H):
    area_year = (
        m.groupby(["Investment area", "Year"], as_index=False)["Amount"].sum()
    )
    area_year = area_year[area_year["Investment area"].isin(ordered_areas)]
    if _sel:
        _pred = alt.FieldOneOfPredicate(field="Investment area", oneOf=_sel)
        traj_op = alt.condition(_pred, alt.value(1), alt.value(0.12))
        traj_sw = alt.condition(_pred, alt.value(3), alt.value(1.8))
        # y-axis rescales to the selected area(s) +20% headroom; the dimmed
        # context lines clip at the frame (mark clip=True below)
        _ymax = area_year.loc[
            area_year["Investment area"].isin(_sel), "Amount"].max()
        traj_scale = (alt.Scale(domain=[0, float(_ymax) * 1.2])
                      if pd.notna(_ymax) and _ymax > 0 else alt.Undefined)
    else:
        traj_op, traj_sw = alt.value(1), alt.value(2.2)
        traj_scale = alt.Undefined
    traj = (
        alt.Chart(area_year)
        .mark_line(point=True, clip=True)
        .encode(
            x=alt.X("Year:O", axis=YEAR_AXIS),
            y=alt.Y("Amount:Q", title=None, scale=traj_scale,
                    axis=alt.Axis(format="~s",
                                  labelExpr='replace(datum.label, "G", "bn")')),
            color=alt.Color("Investment area:N", scale=area_scale, legend=None),
            opacity=traj_op,
            strokeWidth=traj_sw,
            tooltip=["Investment area", "Year",
                     alt.Tooltip("Amount:Q", format=",.0f")],
        )
        .properties(height=320,
                    title=alt.TitleParams("Yearly trajectory by area", fontSize=13))
    )
    st.altair_chart(traj, use_container_width=True)
    st.caption("Same colors as the donut legend — one legend serves both. "
               "Shows each area's scale and its scale-down over the term.")

# ---------------- small multiples ----------------
st.markdown(f"#### Funding by investment area, {TERM} (US$ per year)")

funder_scale = alt.Scale(
    domain=["USG", lib.GOV_LABEL], range=[PAL["usg"], PAL["gov"]]
)

# ---- 2026 mix of Other commodities (Appendix 2) for the in-grid micro-donut ----
MIX_COLORS = {
    "HIV (ARVs, PrEP, tests)": PAL["usg"],
    "HIV & TB": "#86b6ef",
    "Malaria": "#1baf7a",
    "TB": "#eda100",
    "MCH": "#e87ba4",
    "Distribution & logistics": "#7c6ee6" if PAL["dark"] else "#4a3aa7",
    "Other": PAL["muted"],
}


def commodity_bucket(item: str) -> str:
    t = item.lower()
    if "hiv" in t and "tb" in t:
        return "HIV & TB"
    if any(k in t for k in ["arv", "prep", "buffer", "hiv"]):
        return "HIV (ARVs, PrEP, tests)"
    if any(k in t for k in ["malaria", "llin", "smc", "irs", "artesunate", "iptp",
                            "acts", "rdt"]):
        return "Malaria"
    if "tb" in t:
        return "TB"
    if any(k in t for k in ["mch", "mnch", "maternal"]):
        return "MCH"
    if any(k in t for k in ["distribution", "warehous", "logistic", "icl"]):
        return "Distribution & logistics"
    return "Other"


@st.cache_data
def commodity_mix(cty: str):
    """Donut source + the total of any App.2 rows printed as SEPARATE tables
    (e.g. Uganda's MCH equipment/infrastructure), which are excluded from the
    donut so it reconciles to the Other Commodities 2026 line item."""
    tidy = lib.load_budget_tidy()
    mx = tidy[
        (tidy["Country"] == cty)
        & tidy["Row type"].str.startswith("Appendix detail")
        & (tidy["Unit"] == "USD")
        & (tidy["Year"] == 2026)
        & (tidy["Investment area"] == "Other commodities")
    ].copy()
    if mx.empty:
        return mx, 0.0
    sep = mx["Category (as printed in MoU)"].str.contains(
        "separate table", case=False, na=False
    )
    sep_total = float(mx.loc[sep, "Amount"].sum())
    mx = mx[~sep]
    mx["Item"] = (
        mx["Category (as printed in MoU)"].str.split(":", n=1).str[-1].str.strip()
    )
    mx["Bucket"] = mx["Item"].map(commodity_bucket)
    out = mx.groupby("Bucket")["Amount"].sum().reset_index()
    out["Share"] = out["Amount"] / out["Amount"].sum()
    return out, sep_total


mix, mix_sep_total = commodity_mix(country)

# Countries where App.2 legitimately does NOT equal the 2026 line item, per the
# MoU's own text — shown under the donut instead of the generic delta warning.
MIX_RECON_NOTES = {
    "Rwanda": "App. 2 prints the full $11.47M annual commodity basket; per §2.3.2, "
              "50% of it is funded by the separate Bridge Plan, so this MoU's 2026 "
              "line item is the other half ($5.74M). The mix shares still apply.",
}


def mix_recon_caption(cty: str, donut_total: float, sep_total: float) -> str:
    """One-line reconciliation of the donut total vs the 2026 USG line item."""
    line26 = df[
        (df["Country"] == cty) & (df["Investment area"] == "Other commodities")
        & (df["Year"] == 2026) & (df["Funder"] == "USG")
    ]["Amount"].sum()
    if cty in MIX_RECON_NOTES:
        txt = "⚠️ " + MIX_RECON_NOTES[cty]
    elif abs(donut_total - line26) < 10_000:
        txt = f"Items sum to the 2026 USG line item ({lib.fmt_usd(line26)})."
    else:
        txt = (f"⚠️ App. 2 items sum to {lib.fmt_usd(donut_total)} vs "
               f"{lib.fmt_usd(line26)} 2026 line item — unexplained gap.")
    if sep_total:
        txt += (f" Excludes {lib.fmt_usd(sep_total)} of MCH equipment & "
                "infrastructure printed as separate App. 2 tables (not part of "
                "this line item).")
    return txt


def mix_donut(mx: pd.DataFrame) -> alt.Chart:
    # Buckets in size order so the clockwise arcs read large-to-small — colors
    # stay fixed per bucket because they're looked up, not positional.
    # No Vega legend: with fixed pixel radii and a container-driven width, a
    # bottom legend's height varies with wrapping and the ring ends up drawn
    # over the labels at grid widths. The legend is plain HTML below the chart
    # (mix_legend_html), which wraps cleanly and can never collide with the ring.
    order = (
        mx.sort_values("Amount", ascending=False)["Bucket"].tolist()
    )
    arcs = (
        alt.Chart(mx)
        # Fixed pixel radii: the ring keeps its size no matter how much space the
        # title takes, and the centre hole (88px across) always fits the label.
        .mark_arc(innerRadius=44, outerRadius=68, stroke=PAL["surface"], strokeWidth=2)
        .encode(
            theta=alt.Theta("Amount:Q"),
            color=alt.Color(
                "Bucket:N",
                scale=alt.Scale(domain=order,
                                range=[MIX_COLORS[b] for b in order]),
                legend=None,
            ),
            order=alt.Order("Amount:Q", sort="descending"),
            tooltip=["Bucket", alt.Tooltip("Amount:Q", format=",.0f", title="US$ 2026"),
                     alt.Tooltip("Share:Q", format=".0%")],
        )
    )
    center = (
        alt.Chart(pd.DataFrame({"label": [lib.fmt_usd(mx["Amount"].sum())]}))
        .mark_text(fontSize=12, fontWeight="bold", color=PAL["ink"])
        .encode(text="label:N")
    )
    return (arcs + center).properties(
        height=168,
        title=alt.TitleParams("Other commodities — 2026 mix (USG, App. 2)", fontSize=13),
    )


def mix_legend_html(mx: pd.DataFrame) -> str:
    """Wrapping chip legend for the mix donut, large-to-small like the arcs.

    Identity is carried by the colored dot; the text stays in ink colors.
    Rendered outside the chart so it can never overlap the ring."""
    rows = mx.sort_values("Amount", ascending=False)
    chips = "".join(
        "<span style='display:inline-flex;align-items:center;white-space:nowrap;"
        "margin:0 12px 3px 0'>"
        f"<span style='width:8px;height:8px;border-radius:50%;flex:none;"
        f"background:{MIX_COLORS[r.Bucket]};display:inline-block;margin-right:5px'></span>"
        f"<span style='color:{PAL['ink']}'>{r.Bucket}</span>&nbsp;"
        f"<span style='color:{PAL['muted']}'>{lib.fmt_usd(r.Amount)} · {r.Share:.0%}</span>"
        "</span>"
        for r in rows.itertuples()
    )
    return (
        "<div style='font-size:11px;line-height:1.6;margin:-10px 0 2px'>"
        + chips + "</div>"
    )


@st.cache_data
def strategic_areas(cty: str) -> pd.DataFrame:
    """Strategic-investment detail harvested from every MoU's Sec 2.6:
    Cameroon has a priced domain x FY table; CIV/Rwanda print per-item prices
    in the narrative; the rest name their areas without pricing them."""
    sa = pd.read_csv(lib.DATA / "strategic_areas.csv")
    return sa[sa["Country"] == cty].sort_values("Order")


strat = strategic_areas(country)

# Build the panel sequence: the mix donut slots in right after Other commodities
# and the strategic-domain panel right after Strategic assistance, so the grid
# still ends as a full block.
# Panels ordered big -> small by 5-year total (ordered_areas = the donut's
# large-to-small ordering, so grid and legend agree). Companion panels stay
# glued to their parents: the commodity-mix donut follows Other commodities,
# the strategic-domain panel follows Strategic assistance.
panels = []
for a in ordered_areas:
    panels.append(("area", a))
    if a == "Other commodities" and not mix.empty:
        panels.append(("mix", None))
    if a == "Strategic assistance / investment" and len(strat):
        panels.append(("strat", None))
if panels:  # the aggregate of all subsequent category panels leads the grid
    panels.insert(0, ("area", "All areas combined"))

# Each panel lives in its own bordered box of identical height: taller charts
# (more square at grid widths) with reserved room for notes beneath. Long
# notes scroll inside the box rather than distorting the grid.
PANEL_H = 370   # box height, identical for every panel (was 470)
CHART_H = 280   # chart height inside the box — unchanged from the original


def render_area_panel(a: str) -> None:
    if a == "All areas combined":
        # aggregate of every category below; footnotes for the headline totals
        # are already shown above the grid, so none repeated here
        sub = df[(df["Country"] == country)
                 & (df["Investment area"] == "All areas combined")
                 & (df["Funder"].isin(funders))].copy()
        panel_fns, note_tt = [], []
    else:
        sub = lib.attach_budget_notes(m[m["Investment area"] == a], a)
        panel_fns = lib.budget_footnotes(area=a, country=country, funders=funders)
        note_tt = [alt.Tooltip("MoU footnote:N")] if panel_fns else []
    if unit == "US$" and panel_style == "Stacked area":
        sub_f = sub.groupby(["Funder", "Year"], as_index=False)["Amount"].sum()
        sub_f["ord"] = (sub_f["Funder"] != "USG").astype(int)  # USG at the bottom
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
                tooltip=["Funder", "Year",
                         alt.Tooltip("Amount:Q", format=",.0f")],
            )
            .properties(height=CHART_H, title=alt.TitleParams(a, fontSize=13))
        )
        # per-year labels: each band as a share of the 2026 COMBINED level
        # (same denominator as the dotted reference) - the two bands sum to
        # "this year vs 2026", so >100% = growth, <100% = shortfall. <5% hidden.
        c26 = sub.loc[sub["Year"] == 2026, "Amount"].sum()
        if len(funders) > 1 and c26 > 0:
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
        # reference: the 2026 COMBINED level (USG + govt where the govt already
        # funds in 2026) held flat -- the top edge is combined, so like for like
        if show_usg_ref:
            if c26 > 0:
                ref = pd.DataFrame(
                    {"Year": sorted(sub["Year"].unique()), "Amount": c26})
                ch = ch + (
                    alt.Chart(ref)
                    .mark_line(strokeDash=[2, 2], strokeWidth=1.4,
                               color=PAL["muted"], opacity=0.9)
                    .encode(x=alt.X("Year:O", axis=YEAR_AXIS), y="Amount:Q",
                            tooltip=[alt.Tooltip(
                                "Amount:Q", format=",.0f",
                                title="2026 combined level (reference)")])
                )
        st.altair_chart(ch, use_container_width=True)
        if panel_fns:
            st.markdown(lib.footnote_block(panel_fns, size_px=10),
                        unsafe_allow_html=True)


def render_mix_panel() -> None:
    st.altair_chart(
        mix_donut(mix).properties(height=CHART_H - 20), use_container_width=True)
    st.markdown(lib.md(mix_legend_html(mix)), unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:10px;color:{PAL["muted"]};line-height:1.25">'
        "⚠️ 2026 snapshot (App. 2) — this split is not "
        "published in the yearly data for 2027–30. "
        f"{lib.md(mix_recon_caption(country, mix['Amount'].sum(), mix_sep_total))}"
        "</div>",
        unsafe_allow_html=True,
    )


STRAT_COLORS = ["#3b82c4", "#1baf7a", "#eda100", "#e87ba4", "#7c6ee6",
                "#c25b4e", "#4fb7c9", "#a3a832", "#b06fc4", "#8a8a8a"]


def render_strat_panel() -> None:
    fy_cols = ["FY26", "FY27", "FY28", "FY29", "FY30"]
    priced = strat.dropna(subset=fy_cols, how="all")
    priced = priced[pd.to_numeric(priced["FY26"], errors="coerce").notna()]
    if len(priced):  # Cameroon-style: full priced domain table -> donut
        d = priced.copy()
        d["Total"] = d[fy_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)
        d = d.sort_values("Total", ascending=False)
        d["Share"] = d["Total"] / d["Total"].sum()
        order = d["Item"].tolist()
        arcs2 = (
            alt.Chart(d)
            .mark_arc(innerRadius=44, outerRadius=68, stroke=PAL["surface"],
                      strokeWidth=2)
            .encode(
                theta=alt.Theta("Total:Q"),
                color=alt.Color("Item:N",
                                scale=alt.Scale(domain=order,
                                                range=STRAT_COLORS[:len(order)]),
                                legend=None),
                order=alt.Order("Total:Q", sort="descending"),
                tooltip=["Item",
                         alt.Tooltip("Total:Q", format=",.0f", title="US$ 2026-30"),
                         alt.Tooltip("Share:Q", format=".0%")],
            )
        )
        center2 = (
            alt.Chart(pd.DataFrame({"label": [lib.fmt_usd(d["Total"].sum())]}))
            .mark_text(fontSize=12, fontWeight="bold", color=PAL["ink"])
            .encode(text="label:N")
        )
        st.altair_chart(
            (arcs2 + center2).properties(
                height=CHART_H - 20,
                title=alt.TitleParams("Strategic investments — domain split (§2.6)",
                                      fontSize=13)),
            use_container_width=True,
        )
        chips = "".join(
            "<div style='margin:0 0 3px'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:"
            f"{STRAT_COLORS[order.index(r.Item)]};display:inline-block;"
            "margin-right:5px'></span>"
            f"<span style='color:{PAL['ink']}'>{r.Item}</span> "
            f"<span style='color:{PAL['muted']}'>{lib.fmt_usd(r.Total)} · "
            f"{r.Share:.0%}</span></div>"
            for r in d.itertuples()
        )
        st.markdown(f"<div style='font-size:11px;line-height:1.45'>{chips}</div>",
                    unsafe_allow_html=True)
        st.markdown(lib.md(
            f'<div style="font-size:10px;color:{PAL["muted"]};line-height:1.25">'
            f"{strat.iloc[0]['Source']} — {strat.iloc[0]['Note']}.</div>"),
            unsafe_allow_html=True)
    else:  # named list (with per-item printed prices where the MoU gives them)
        items = "".join(
            "<div style='margin:0 0 5px'>"
            f"<span style='color:{PAL['ink']};font-weight:600'>{r['Item']}</span>"
            + (f" <span style='color:{PAL['muted']}'>— {r['Price (as printed)']}"
               "</span>" if str(r["Price (as printed)"]) not in ("", "nan") else "")
            + "</div>"
            for _, r in strat.iterrows()
        )
        notes = " ".join(n for n in strat["Note"].dropna().astype(str) if n)
        any_priced = strat["Price (as printed)"].astype(str).str.strip().replace(
            "nan", "").str.len().gt(0).any()
        tail = ("Prices as printed in the narrative — no domain × year table"
                if any_priced else "The MoU does not price these individually")
        st.markdown(lib.md(
            "<div style='font-size:13px;font-weight:700;margin-bottom:6px'>"
            "Strategic investments — named areas (§2.6)</div>"
            f"<div style='font-size:11.5px;line-height:1.4'>{items}</div>"
            f'<div style="font-size:10px;color:{PAL["muted"]};margin-top:6px">'
            f"{strat.iloc[0]['Source']}. {tail}"
            f"{' — ' + notes if notes else ''}.</div>"),
            unsafe_allow_html=True)


for start in range(0, len(panels), 3):
    row_cols = st.columns(3)
    for j, (kind, a) in enumerate(panels[start:start + 3]):
        with row_cols[j], st.container(border=True, height=PANEL_H):
            if kind == "mix":
                render_mix_panel()
            elif kind == "strat":
                render_strat_panel()
            else:
                render_area_panel(a)

st.markdown(
    f'<span style="color:{PAL["usg"]};font-weight:600">▮ USG (bottom)</span> &nbsp; '
    f'<span style="color:{PAL["gov"]};font-weight:600">▮ Govt, stacked on top — '
    'top edge = combined funding</span> &nbsp; '
    f'<span style="color:{PAL["muted"]}">·· 2026 combined level (reference)</span> '
    '<span style="color:white;font-weight:700">%</span> '
    f'<span style="color:{PAL["muted"]};font-size:12px">= share of the 2026 '
    "combined level - the two bands sum to that year vs 2026 (>100% = growth, "
    '<100% = shortfall; labels under 5% hidden)</span> '
    f'<span style="color:{PAL["muted"]};font-size:12px">(printed/imputed/baseline '
    'components are summed in this view — see the captions above for the split)</span>',
    unsafe_allow_html=True,
)

# printed footnotes whose investment area has no dollar panel above (e.g. Côte
# d'Ivoire's orphan asterisk on its FTE-only frontline-worker table)
shown_areas = {a for kind, a in panels if kind == "area"}
leftover = [
    n for n in lib.budget_footnotes(country=country, funders=funders)
    if n["Area"] not in shown_areas and n["Area"] != "All areas combined"
]
if leftover:
    st.markdown(
        lib.footnote_block([{**n, "Country": n["Area"]} for n in leftover]),
        unsafe_allow_html=True,
    )

# ---------------- detail table ----------------
with st.expander("Line-item detail (as printed in the MoU, with caveats)"):
    detail = lib.load_budget_tidy()
    detail = detail[detail["Country"] == country]

    # filter row
    f1, f2, f3, f4 = st.columns([2, 1.4, 2, 2])
    with f1:
        f_area = st.multiselect("Investment area", sorted(detail["Investment area"].unique()),
                                placeholder="All areas")
    with f2:
        f_funder = st.multiselect("Funder", sorted(detail["Funder"].unique()),
                                  placeholder="All funders")
    with f3:
        f_rowtype = st.multiselect("Row type", sorted(detail["Row type"].unique()),
                                   placeholder="All row types")
    with f4:
        f_text = st.text_input("Search category / notes", "",
                               placeholder="e.g. ARV, buffer, FTE…")
    if f_area:
        detail = detail[detail["Investment area"].isin(f_area)]
    if f_funder:
        detail = detail[detail["Funder"].isin(f_funder)]
    if f_rowtype:
        detail = detail[detail["Row type"].isin(f_rowtype)]
    if f_text:
        mask = (
            detail["Category (as printed in MoU)"].str.contains(f_text, case=False, na=False)
            | detail["Source note"].astype(str).str.contains(f_text, case=False, na=False)
            | detail[lib.FOOTNOTE_COL].astype(str).str.contains(f_text, case=False, na=False)
        )
        detail = detail[mask]

    st.dataframe(
        detail,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="localized"),
            "Source (MoU PDF)": st.column_config.LinkColumn("Source (MoU PDF)",
                                                            display_text="open PDF"),
        },
    )
    st.caption(
        f"{len(detail):,} rows shown. Click any column header to sort; the 🔍 icon in the "
        "table toolbar does a live full-text search. Only rows with Row type = 'Line item' "
        "(plus existing-government rows and 'Line item - outside headline total', which "
        "Uganda alone carries) feed the charts above — and, when the sidebar "
        "toggle is on, rows with Row type = 'Imputed (derived - not printed in MoU)', "
        "whose Source note records the FTEs, rate and confidence used. Other row types "
        "are excluded to avoid double counting. 'MoU footnote (verbatim)' holds the notes "
        "the MoU itself prints on its tables, carried across the full funding line; "
        "'MoU footnote location' pinpoints the marked cells."
    )
