"""MoU dashboard — Overview across all countries."""
import altair as alt
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(
    page_title="USG MoU dashboard — Overview",
    page_icon="🌍",
    layout="wide",
)

st.title("USG bilateral health MoUs — funding across all countries")
st.caption(
    "Five-year cooperation plans (2026–2030) signed under the America First Global Health "
    "Strategy. This page compares the 16 countries whose full MoU text is public. "
    "Amounts come from each MoU's co-funding appendix; 'Government' = new co-financing "
    "*plus* existing government funding where the MoU tabulates it. "
    "See **Sources & methodology** for links and caveats."
)


@st.cache_data
def data(include_imputed: bool, include_baseline: bool):
    df = lib.load_budget_series()
    if not include_imputed:
        df = df[df["Basis"] != lib.BASIS_IMPUTED]
    if not include_baseline:
        df = df[~df["Basis"].isin(lib.BASELINE_BASES)]
    # Collapse Basis so each Country x Area x Year x Funder is one line/bar again
    # ("All areas combined" can carry several rows per year).
    df = df.groupby(["Country", "Investment area", "Year", "Funder"],
                    as_index=False)["Amount"].sum()
    return lib.add_share(df)


PAL = lib.palette()  # follows the active (system-preference) theme

# Year axis style: bigger, bold, -45°
YEAR_AXIS = alt.Axis(labelAngle=-45, labelFontSize=14, labelFontWeight="bold", title=None)

# Line hover: lift the hovered country out of the grey field. empty=False so an
# untouched chart stays uniformly grey rather than treating "nothing selected"
# as "everything selected".
hover = alt.selection_point(fields=["Country"], on="pointerover",
                            clear="pointerout", empty=False)

# ---------------- controls ----------------
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    unit = st.radio("Unit", ["US$", "% of combined"], horizontal=True)
    include_imputed = st.toggle(
        "Incl. imputed govt $", value=True,
        help="Government FTE commitments priced at government/USG unit rates where "
             "the MoU prints FTEs but no dollars (Cameroon, Ethiopia labs, Rwanda, "
             "Côte d'Ivoire, Lesotho) — or, for Uganda, prices only each year's "
             "new cohort (absorbed-cohort continuation imputed). See Sources & "
             "methodology.",
    )
    include_baseline = st.toggle(
        "Incl. pre-MoU / existing funding $", value=True,
        help=lib.md("Existing government workforce valued at each MoU's own rates "
             "(~$3.09bn across nine countries) plus printed pre-MoU government "
             "funding (~$1.62bn across twelve; where a MoU's Existing column rolls "
             "prior-year commitments forward, only the flat 2026 base counts). "
             "Baseline effort, not MoU co-financing."),
    )
df = data(include_imputed, include_baseline)
with c1:
    area = st.selectbox("Investment area", lib.area_options(df), index=0)
with c3:
    countries = st.multiselect(
        "Countries", sorted(df["Country"].unique()), default=sorted(df["Country"].unique())
    )

NO_HIGHLIGHT = "— all countries —"
highlight = st.selectbox(
    "Highlight one country", [NO_HIGHLIGHT] + sorted(countries),
    help="Pick a country to draw it in colour against the rest in grey — the clearest "
         "way to read one trajectory against the field. Leave on 'all countries' to "
         "compare everything at once.",
)
if highlight not in countries:
    highlight = NO_HIGHLIGHT

m = df[(df["Investment area"] == area) & (df["Country"].isin(countries))]

# ---------------- KPIs ----------------
tot_usg = m.loc[m["Funder"] == "USG", "Amount"].sum()
tot_gov = m.loc[m["Funder"] == lib.GOV_LABEL, "Amount"].sum()
k1, k2, k3, k4 = st.columns(4)
k1.metric("USG, full term", lib.fmt_usd(tot_usg))
k2.metric("Government, full term", lib.fmt_usd(tot_gov))
combined = tot_usg + tot_gov
k3.metric("Combined", lib.fmt_usd(combined))
k4.metric("USG share of combined", f"{100 * tot_usg / combined:.0f}%" if combined else "–")
caveats = []
if include_imputed:
    caveats.append("imputed govt $")
if include_baseline:
    caveats.append("pre-MoU/existing funding $")
if caveats:
    st.caption(lib.md(
        "Includes " + " and ".join(caveats) + " — see **Sources & methodology**."
    ))

# Sixteen countries is more than colour can separate, so the chart is a GREY
# FIELD: every line recessive grey, identity carried by the tooltip, by hovering
# a line (it lifts to ink), and by the "Highlight one country" picker, which
# draws the chosen country in its own hue on top of the field. No legend — a
# legend of sixteen identical grey strokes would name nothing.
_pal_country = PAL["country"]
CONTEXT_GREY = "#57565a" if PAL["dark"] else "#c9c7c0"


def trend_chart(plot: pd.DataFrame, y_enc, tooltip, height: int = 400):
    """A grey field of trajectories, with one country picked out.

    No highlight: all lines grey; hovering one lifts it to ink with a thicker
    stroke (empty=False keeps the field grey until the pointer lands). With a
    highlight: the other fifteen stay grey and the chosen country is drawn on
    top in its own colour. Grey lines keep their tooltips throughout.
    """
    x_enc = alt.X("Year:O", axis=YEAR_AXIS)
    if highlight == NO_HIGHLIGHT:
        field = (
            alt.Chart(plot)
            .mark_line(point=alt.OverlayMarkDef(color=CONTEXT_GREY, size=22),
                       strokeWidth=1.6, opacity=0.65, color=CONTEXT_GREY)
            .encode(x=x_enc, y=y_enc, detail="Country:N")
        )
        # A thin grey line is a hard pointer target, so a ~12px invisible band
        # rides on every line to catch the hover and carry the tooltip …
        hit = (
            alt.Chart(plot)
            .mark_line(strokeWidth=13, opacity=0.01)
            .encode(x=x_enc, y=y_enc, detail="Country:N", tooltip=tooltip)
            .add_params(hover)
        )
        # … and the hovered country is re-drawn in ink on top.
        lifted = (
            alt.Chart(plot)
            .mark_line(point=alt.OverlayMarkDef(color=PAL["ink"]),
                       strokeWidth=3.2, color=PAL["ink"])
            .encode(x=x_enc, y=y_enc, detail="Country:N", tooltip=tooltip)
            .transform_filter(hover)
        )
        return (field + lifted + hit).properties(height=height)
    rest = plot[plot["Country"] != highlight]
    pick = plot[plot["Country"] == highlight]
    context = (
        alt.Chart(rest).mark_line(point=False, strokeWidth=1.4, opacity=0.55,
                                  color=CONTEXT_GREY)
        .encode(x=x_enc, y=y_enc, detail="Country:N", tooltip=tooltip)
    )
    _hl = _pal_country.get(highlight, PAL["usg"])
    lead = (
        alt.Chart(pick).mark_line(
            point=alt.OverlayMarkDef(color=_hl), strokeWidth=3.6, color=_hl)
        .encode(x=x_enc, y=y_enc, tooltip=tooltip)
    )
    return (context + lead).properties(height=height)


def nudge_ties(plot: pd.DataFrame, col: str, step: float = 0.008) -> pd.DataFrame:
    """Separate exactly-overlapping lines so identical shares stay distinguishable.

    Countries whose value is identical in a given year are nudged apart by <1pp
    each (downward near the top of the scale, upward near the bottom) purely for
    display; tooltips always show the true value.
    """
    import numpy as np

    plot = plot.sort_values("Country").copy()
    plot["_r"] = plot[col].round(4)
    plot["_rank"] = plot.groupby(["Year", "_r"]).cumcount()
    direction = np.where(plot[col] >= 0.5, -1.0, 1.0)  # nudge inward from either edge
    plot[col + "Disp"] = (plot[col] + plot["_rank"] * step * direction).clip(0, 1)
    return plot.drop(columns=["_r", "_rank"])


# ---------------- chart 1: trajectories by year ----------------
st.subheader(f"{area} — by year"
             + (f"  ·  {highlight} against the other {len(countries) - 1}"
                if highlight != NO_HIGHLIGHT else ""))
if unit == "US$":
    funder_pick = st.radio(
        "Funder", ["USG", lib.GOV_LABEL, "Combined"], horizontal=True, key="ov_funder"
    )
    if funder_pick == "Combined":
        plot = (
            m.groupby(["Country", "Year"])["Amount"].sum().reset_index()
        )
    else:
        plot = m[m["Funder"] == funder_pick]
    plot = lib.attach_budget_notes(plot, area)
    tt = ["Country", "Year", alt.Tooltip("Amount:Q", format=",.0f")]
    if (plot["MoU footnote"] != "").any():
        tt.append(alt.Tooltip("MoU footnote:N"))
    y_usd = alt.Y("Amount:Q", title="US$ per year",
                  axis=alt.Axis(format="~s",
                                labelExpr='replace(datum.label, "G", "bn")'))
    st.altair_chart(trend_chart(plot, y_usd, tt), use_container_width=True)
    st.caption(lib.md(
        "Sixteen trajectories, one grey field — **hover any line** to lift it out and "
        "read its country in the tooltip, or **highlight one country** above to draw "
        "it in colour against the rest. Sixteen is more than distinct colours can "
        "separate, so identity lives in the hover and the picker, not a legend."
    ))
else:
    st.caption(
        "Lines show the **USG share** of each year's combined USG + government funding "
        "(government share = 100% − USG). Dashed rule = 50%: below it, the government is "
        "the majority funder. Hover a line to lift it out of the grey field, or use "
        "the highlight picker above. Countries with *identical* shares are nudged "
        "apart by <1pp so every line stays visible — tooltips show the true value."
    )
    plot = nudge_ties(m[m["Funder"] == "USG"].dropna(subset=["Share"]), "Share")
    plot = lib.attach_budget_notes(plot, area)
    share_tt = [
        "Country",
        "Year",
        alt.Tooltip("Share:Q", format=".0%", title="USG share (true)"),
        alt.Tooltip("Amount:Q", title="USG US$", format=",.0f"),
        alt.Tooltip("Combined:Q", title="Combined US$", format=",.0f"),
    ]
    if (plot["MoU footnote"] != "").any():
        share_tt.append(alt.Tooltip("MoU footnote:N"))
    y_share = alt.Y("ShareDisp:Q", title="USG share of combined",
                    axis=alt.Axis(format=".0%"), scale=alt.Scale(domain=[0, 1]))
    base = trend_chart(plot, y_share, share_tt)
    rule = alt.Chart(pd.DataFrame({"y": [0.5]})).mark_rule(
        strokeDash=[4, 4], color=PAL["muted"]
    ).encode(y="y:Q")
    st.altair_chart(base + rule, use_container_width=True)

# printed MoU footnotes for this selection (each applies across the full line)
fns = [n for n in lib.budget_footnotes(area=area) if n["Country"] in countries]
if fns:
    st.markdown(lib.footnote_block(fns), unsafe_allow_html=True)

# ---------------- chart 2: 5-year totals ----------------
st.subheader(f"{area} — totals over each MoU's full term, by country")
st.caption("Every MoU runs 2026–2030 except Botswana, whose term is 2026–2028 — "
           "its bar covers three years, not five.")
tot = lib.five_year_totals(m, area)
funder_color = alt.Color(
    "Funder:N",
    scale=alt.Scale(domain=["USG", lib.GOV_LABEL], range=[PAL["usg"], PAL["gov"]]),
    legend=alt.Legend(orient="bottom", title=None, labelLimit=0),
)
if unit == "US$":
    ch2 = (
        alt.Chart(tot)
        .mark_bar()
        .encode(
            y=alt.Y("Country:N", sort="-x", title=None,
                    axis=alt.Axis(labelFontSize=13, labelOverlap=False)),
            x=alt.X("Amount:Q", title="US$, 2026–2030", axis=alt.Axis(format="~s", labelExpr='replace(datum.label, "G", "bn")')),
            color=funder_color,
            tooltip=["Country", "Funder", alt.Tooltip("Amount:Q", format=",.0f")],
        )
        .properties(height=max(340, 34 * len(countries)))
    )
else:
    ch2 = (
        alt.Chart(tot.dropna(subset=["Share"]))
        .mark_bar()
        .encode(
            y=alt.Y("Country:N", title=None,
                    axis=alt.Axis(labelFontSize=13, labelOverlap=False)),
            x=alt.X("Share:Q", title="Share of combined, 2026–2030",
                    axis=alt.Axis(format=".0%"), stack="normalize"),
            color=funder_color,
            tooltip=["Country", "Funder", alt.Tooltip("Share:Q", format=".0%"),
                     alt.Tooltip("Amount:Q", format=",.0f")],
        )
        .properties(height=max(340, 34 * len(countries)))
    )
st.altair_chart(ch2, use_container_width=True)

# ---------------- table & downloads ----------------
with st.expander("Data behind these charts"):
    show = m.pivot_table(
        index=["Country", "Funder"], columns="Year", values="Amount", aggfunc="sum"
    ).reset_index()
    show.columns = [str(c) for c in show.columns]
    year_cols = [c for c in show.columns if c.isdigit()]
    st.dataframe(
        show,
        use_container_width=True,
        hide_index=True,
        column_config={c: st.column_config.NumberColumn(c, format="localized")
                       for c in year_cols},
    )
    st.caption("Click any column header to sort (A–Z / small–big).")
    st.download_button(
        "Download full tidy budget table (CSV)",
        (lib.DATA / "budget_tidy.csv").read_bytes(),
        file_name="budget_tidy.csv",
        mime="text/csv",
    )

st.info(lib.md(
    "Countries without a published existing-funding split (Nigeria, Ethiopia, Rwanda) "
    "show new co-financing only — their true government shares are understated. "
    "Government $ for frontline labs & healthcare workers in Cameroon, Ethiopia, "
    "Rwanda, Uganda, Côte d'Ivoire and Lesotho are imputed from FTE commitments "
    "when the toggle above is on. Full caveats on the **Sources & methodology** page."
))
