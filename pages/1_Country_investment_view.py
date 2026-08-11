"""MoU dashboard — Country investment view (small multiples per investment area)."""
import altair as alt
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(page_title="MoU dashboard — Country investment view", page_icon="💵",
                   layout="wide")

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
         "t stay funded in every later year. Dashed lines. See Sources & methodology.",
)
include_baseline = st.sidebar.toggle(
    "Include pre-MoU / existing funding $", value=True,
    help="Two pre-MoU components: the existing government workforce the MoU "
         "tabulates, valued at reference rates (dotted; CIV, Uganda, Mozambique, "
         "Liberia), and the printed existing commodity funding carried from 2026 "
         "(dash-dot; Kenya, Uganda, CIV, Liberia, Mozambique). Baseline effort, "
         "not MoU co-financing.",
)
df = data(include_imputed, include_baseline)
meta = countries_meta()
PAL = lib.palette()  # follows the active (system-preference) theme

country = st.sidebar.selectbox("Country", sorted(df["Country"].unique()))
unit = st.sidebar.radio("Unit", ["US$", "% of combined"])
funder_pick = st.sidebar.radio("Funder", ["USG", "Govt (existing + new)", "Both"], index=2)
FUNDER_MAP = {"USG": ["USG"], "Govt (existing + new)": [lib.GOV_LABEL],
              "Both": ["USG", lib.GOV_LABEL]}
funders = FUNDER_MAP[funder_pick]

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
usg_t = cc.loc[cc["Funder"] == "USG", "Amount"].sum()
gov_t = cc.loc[cc["Funder"] == lib.GOV_LABEL, "Amount"].sum()
comb_t = usg_t + gov_t
k1, k2, k3, k4 = st.columns(4)
k1.metric("USG, 2026–2030", lib.fmt_usd(usg_t))
k2.metric("Govt co-financing (new + existing)", lib.fmt_usd(gov_t))
k3.metric("Combined (itemised)", lib.fmt_usd(comb_t))
k4.metric("USG share of combined", f"{100 * usg_t / comb_t:.0f}%" if comb_t else "–")

# flag the imputed / baseline components of the headline government figure
imp_t = lib.imputed_total(df, country)
base_t = (lib.imputed_total(df, country, lib.BASIS_BASELINE)
          + lib.imputed_total(df, country, lib.BASIS_PRINTED_EXISTING))
if include_imputed and imp_t > 0:
    st.caption(
        f"⚠️ The government figures include **{lib.fmt_usd(imp_t)} of imputed $** "
        "for frontline labs & healthcare workers — " + lib.IMPUTED_CAPTION
    )
if include_baseline and base_t > 0:
    st.caption(
        f"⚠️ They also include **{lib.fmt_usd(base_t)} of pre-MoU / existing "
        "funding $** — " + lib.BASELINE_CAPTION
    )

# printed MoU footnotes that qualify this country's headline totals
hfns = lib.budget_footnotes(area="All areas combined", country=country)
if hfns:
    st.markdown(lib.footnote_block(hfns), unsafe_allow_html=True)

share = row["USG share"]
st.caption(
    f"For reference, the **KFF headline** for {country} is "
    f"{lib.fmt_usd(row['Total agreement (USD)'])} total — "
    f"{lib.fmt_usd(row['USG (USD)'])} USG / "
    f"{lib.fmt_usd(row['Co-financing (USD)'])} co-financing"
    + (f" ({100 * share:.0f}% USG)" if pd.notna(share) else "")
    + ". KFF counts each MoU's headline pledge, which for some countries is a "
    "domestic-expenditure-increase commitment rather than itemised funding, so it can "
    "differ from the itemised amounts charted on this page — see Sources & methodology."
)

# ---------------- small multiples ----------------
m = df[
    (df["Country"] == country)
    & (df["Funder"].isin(funders))
    & (df["Investment area"] != "All areas combined")
]
areas = [a for a in lib.area_options(m) if a != "All areas combined"]

st.markdown(
    f"#### Funding by investment area, 2026–2030 "
    f"({'US$ per year' if unit == 'US$' else 'share of combined USG + government funding'})"
)

funder_scale = alt.Scale(
    domain=["USG", lib.GOV_LABEL], range=[PAL["usg"], PAL["gov"]]
)
# Solid = printed in the MoU; dashed = imputed from FTE commitments;
# dotted = pre-MoU baseline workforce
basis_dash = alt.StrokeDash(
    "Basis:N",
    scale=alt.Scale(domain=[lib.BASIS_PRINTED, lib.BASIS_IMPUTED, lib.BASIS_BASELINE,
                            lib.BASIS_PRINTED_EXISTING],
                    range=[[1, 0], [6, 4], [2, 3], [8, 3, 2, 3]]),
    legend=None,
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


# Build the panel sequence: the mix donut slots in right after Other commodities,
# so the grid still ends as a full block (typically 3 x 3).
panels = []
for a in areas:
    if m[m["Investment area"] == a]["Amount"].sum() > 0:
        panels.append(("area", a))
        if a == "Other commodities" and not mix.empty:
            panels.append(("mix", None))

cols = st.columns(3)
for i, (kind, a) in enumerate(panels):
    if kind == "mix":
        with cols[i % 3]:
            st.altair_chart(mix_donut(mix), use_container_width=True)
            st.markdown(mix_legend_html(mix), unsafe_allow_html=True)
            st.markdown(
                f'<div style="font-size:10px;color:{PAL["muted"]};line-height:1.25">'
                "⚠️ 2026 snapshot (App. 2) — this split is not "
                "published in the yearly data for 2027–30. "
                f"{mix_recon_caption(country, mix['Amount'].sum(), mix_sep_total)}"
                "</div>",
                unsafe_allow_html=True,
            )
        continue
    sub = lib.attach_budget_notes(m[m["Investment area"] == a], a)
    panel_fns = lib.budget_footnotes(area=a, country=country, funders=funders)
    note_tt = [alt.Tooltip("MoU footnote:N")] if panel_fns else []
    with cols[i % 3]:
        if unit == "US$":
            ch = (
                alt.Chart(sub)
                .mark_line(point=True, strokeWidth=2.5)
                .encode(
                    x=alt.X("Year:O", axis=YEAR_AXIS),
                    y=alt.Y("Amount:Q", title=None, axis=alt.Axis(format="~s", labelExpr='replace(datum.label, "G", "bn")')),
                    color=alt.Color("Funder:N", scale=funder_scale, legend=None),
                    strokeDash=basis_dash,
                    detail="Basis:N",
                    tooltip=["Funder", "Year", alt.Tooltip("Amount:Q", format=",.0f"),
                             "Basis"]
                    + note_tt,
                )
                .properties(height=190, title=alt.TitleParams(a, fontSize=13))
            )
            st.altair_chart(ch, use_container_width=True)
            if panel_fns:
                st.markdown(lib.footnote_block(panel_fns, size_px=10),
                            unsafe_allow_html=True)
        else:
            sub2 = sub.dropna(subset=["Share"])
            if sub2.empty:
                continue
            line = (
                alt.Chart(sub2)
                .mark_line(point=True, strokeWidth=2.5)
                .encode(
                    x=alt.X("Year:O", axis=YEAR_AXIS),
                    y=alt.Y("Share:Q", title=None, axis=alt.Axis(format=".0%"),
                            scale=alt.Scale(domain=[0, 1])),
                    color=alt.Color("Funder:N", scale=funder_scale, legend=None),
                    strokeDash=basis_dash,
                    detail="Basis:N",
                    tooltip=["Funder", "Year", alt.Tooltip("Share:Q", format=".0%"),
                             alt.Tooltip("Amount:Q", format=",.0f"), "Basis"] + note_tt,
                )
                .properties(height=190, title=alt.TitleParams(a, fontSize=13))
            )
            rule = (
                alt.Chart(pd.DataFrame({"y": [0.5]}))
                .mark_rule(strokeDash=[4, 4], color="#898781")
                .encode(y="y:Q")
            )
            st.altair_chart(line + rule, use_container_width=True)
            if panel_fns:
                st.markdown(lib.footnote_block(panel_fns, size_px=10),
                            unsafe_allow_html=True)

st.markdown(
    f'<span style="color:{PAL["usg"]};font-weight:600">— USG</span> &nbsp; '
    f'<span style="color:{PAL["gov"]};font-weight:600">— Govt (existing + new)</span>'
    + (f' &nbsp; <span style="color:{PAL["gov"]};font-weight:600">- - imputed from '
       'FTEs</span>' if include_imputed and imp_t > 0 else "")
    + (f' &nbsp; <span style="color:{PAL["gov"]};font-weight:600">·· / -·- pre-MoU '
       'baseline & existing funding</span>' if include_baseline and base_t > 0 else ""),
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

# ---------------- donut: how the areas compare in size ----------------
st.markdown(f"#### How the investment areas compare, 2026–2030 ({funder_pick})")
donut_src = (
    m.groupby("Investment area")["Amount"].sum().reset_index().query("Amount > 0")
    .sort_values("Amount", ascending=False)
)
donut_total = donut_src["Amount"].sum()
donut_src["Share of total"] = donut_src["Amount"] / donut_total

# Domain in size order -> legend reads large-to-small, matching the clockwise arcs;
# colors stay fixed per area because they're looked up, not positional.
ordered_areas = donut_src["Investment area"].tolist()
area_scale = alt.Scale(
    domain=ordered_areas, range=[PAL["area"][a] for a in ordered_areas]
)
donut_sel = alt.selection_point(fields=["Investment area"], bind="legend")

arcs = (
    alt.Chart(donut_src)
    .mark_arc(innerRadius=78, stroke=PAL["surface"], strokeWidth=2)
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
            alt.Tooltip("Amount:Q", format=",.0f", title="US$ 2026–2030"),
            alt.Tooltip("Share of total:Q", format=".1%"),
        ],
    )
    .add_params(donut_sel)
)
center_df = pd.DataFrame({"label": [lib.fmt_usd(donut_total)]})
center_value = (
    alt.Chart(center_df)
    .mark_text(fontSize=24, fontWeight="bold", color=PAL["ink"], dy=-6)
    .encode(text="label:N")
)
center_sub = (
    alt.Chart(pd.DataFrame({"label": ["2026–2030"]}))
    .mark_text(fontSize=11, color=PAL["muted"], dy=14)
    .encode(text="label:N")
)
donut = (arcs + center_value + center_sub).properties(height=340)

dc1, dc2 = st.columns([3, 2])
with dc1:
    st.altair_chart(donut, use_container_width=True)
with dc2:
    top = donut_src.head(5)
    st.markdown("**Largest areas**")
    for _, r in top.iterrows():
        st.markdown(
            f"- {r['Investment area']}: **{lib.fmt_usd(r['Amount'])}** "
            f"({r['Share of total']:.0%})"
        )
    st.caption(
        "Respects the funder toggle in the sidebar. Legend is ordered large → small, "
        "matching the clockwise arcs — click a legend entry to highlight its segment "
        "(click it again to reset). Hover a segment for details."
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
        "(plus existing-government rows) feed the charts above — and, when the sidebar "
        "toggle is on, rows with Row type = 'Imputed (derived - not printed in MoU)', "
        "whose Source note records the FTEs, rate and confidence used. Other row types "
        "are excluded to avoid double counting. 'MoU footnote (verbatim)' holds the notes "
        "the MoU itself prints on its tables, carried across the full 5-year line; "
        "'MoU footnote location' pinpoints the marked cells."
    )
