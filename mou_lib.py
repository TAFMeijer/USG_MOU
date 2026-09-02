"""Shared data loading & transforms for the MoU dashboard.

Pure pandas — no Streamlit imports — so everything here is unit-testable.
All figures originate from the co-funding appendices of the 16 published
America First bilateral health MoU texts (see data/sources.csv).
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"

YEARS = [2026, 2027, 2028, 2029, 2030]

# Consistent colors across the dashboard
USG_COLOR = "#2a78d6"
GOV_COLOR = "#eb6834"
# Sixteen countries is well past the ~8 hues a reader can tell apart, so identity is
# carried by a COMPOSITE encoding: eight validated hues x two stroke styles. The eight
# hues are the same validated categorical set used for AREA_COLORS (adjacent-pair CVD
# ΔE 9.1 light / 8.4 dark, normal-vision ΔE 19.6 / 19.3 — both modes pass every gate).
# Hue is fixed per country and never cycled or reassigned by rank; the nine countries
# published before September 2026 keep the colours they have always had.
_HUES_LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
               "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
_HUES_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500",
              "#d55181", "#008300", "#9085e9", "#e66767"]
SOLID_COUNTRIES = ["Cameroon", "Côte d'Ivoire", "Ethiopia", "Kenya",
                   "Liberia", "Mozambique", "Nigeria", "Rwanda"]
DASHED_COUNTRIES = ["Botswana", "Burundi", "Eswatini", "Lesotho",
                    "Madagascar", "Malawi", "Sierra Leone", "Uganda"]
# Legend/scale order: the two stroke groups read as blocks rather than interleaving
# same-hue neighbours.
COUNTRY_ORDER = SOLID_COUNTRIES + DASHED_COUNTRIES
SOLID_DASH = [1, 0]
DASH_DASH = [6, 3]
COUNTRY_DASH = {c: SOLID_DASH for c in SOLID_COUNTRIES}
COUNTRY_DASH.update({c: DASH_DASH for c in DASHED_COUNTRIES})
COUNTRY_COLORS = dict(zip(SOLID_COUNTRIES, _HUES_LIGHT))
COUNTRY_COLORS.update(dict(zip(DASHED_COUNTRIES, _HUES_LIGHT)))
COUNTRY_COLORS = {c: COUNTRY_COLORS[c] for c in COUNTRY_ORDER}

# One fixed color per investment area (donut & composition charts)
AREA_COLORS = {
    "Laboratory commodities": "#2a78d6",
    "Laboratory systems": "#86b6ef",
    "Frontline lab workers": "#1baf7a",
    "Frontline healthcare workers": "#008300",
    "Other commodities": "#eb6834",
    "Surveillance & outbreak response": "#e34948",
    "Data systems": "#4a3aa7",
    "Strategic assistance / investment": "#eda100",
    "Management & operations": "#898781",
    "Programme management": "#c3c2b7",
    "Technical assistance": "#e87ba4",
    "Other health sector co-investment": "#52514e",
    # Cameroon's aggregate co-investment rows only. They exist in budget_tidy
    # (Row type "Aggregate co-investment (overlaps itemised rows - do not sum)")
    # and in the explorer's AREA_NOTES, but never reach budget_series, so this
    # area is deliberately absent from AREA_ORDER and never offered as a
    # selection — the color is here for the full-data table alone.
    "Commodities & HRH co-investment": "#b7d3f6",
}

AREA_ORDER = [
    "All areas combined",
    "Laboratory commodities",
    "Laboratory systems",
    "Frontline lab workers",
    "Frontline healthcare workers",
    "Other commodities",
    "Surveillance & outbreak response",
    "Data systems",
    "Strategic assistance / investment",
    "Management & operations",
    "Programme management",
    "Technical assistance",
    "Other health sector co-investment",
]

GOV_LABEL = "Government (new + existing)"

# Basis of each dollar series: printed in the MoU, or imputed from government FTE
# commitments at USG unit rates (analysis/fte_rate_imputation_all.py). Imputed
# rows are appended to the data files by analysis/apply_imputation_to_dashboard.py.
BASIS_PRINTED = "Printed in MoU"
BASIS_IMPUTED = "Imputed from FTEs"
BASIS_BASELINE = "Imputed baseline (pre-MoU)"
BASIS_PRINTED_EXISTING = "Printed in MoU (existing/pre-MoU)"
# Both pre-MoU components, removed together by the baseline toggle:
BASELINE_BASES = [BASIS_BASELINE, BASIS_PRINTED_EXISTING]
IMPUTED_ROW_TYPE = "Imputed (derived - not printed in MoU)"
BASELINE_ROW_TYPE = "Imputed baseline (pre-MoU - derived)"

IMPUTED_CAPTION = (
    "Imputed government $ are **derived, not printed in the MoU**: government FTE "
    "commitments × a $/FTE rate taken from the same MoU's USG side (or peer-country "
    "rates where none exists). Ethiopia's and Kenya's MoUs apply exactly this "
    "arithmetic internally. They are summed into the government band of every "
    "panel; the sidebar toggle takes them back out. Method, rates and confidence "
    "ranges: **Sources & methodology**."
)

BASELINE_CAPTION = (
    "Pre-MoU baseline $ covers two components: the **existing government workforce** "
    "nine MoUs tabulate (2026 'Existing # FTEs Funded' stock — CIV, Uganda, "
    "Mozambique, Liberia, Malawi, Sierra Leone, Burundi, Madagascar, Eswatini — "
    "valued at each MoU's own rates) and the **printed existing government funding** "
    "thirteen MoUs mark as existing rather than new. Baseline effort that predates "
    "the MoU, **not** MoU co-financing. Both sit inside the government band of every "
    "panel; the sidebar toggle removes them together, lowering the band to the "
    "co-financing the MoUs themselves count as new."
)


def load_budget_series() -> pd.DataFrame:
    """Aggregated, safely summable series: Country x Investment area x Year x Funder.

    Carries a `Basis` column (BASIS_PRINTED / BASIS_IMPUTED); pages that offer an
    "include imputed" toggle filter on it before aggregating.
    """
    df = pd.read_csv(DATA / "budget_series.csv")
    df["Funder"] = df["Funder"].replace({"Government": GOV_LABEL})
    if "Basis" not in df.columns:
        df["Basis"] = BASIS_PRINTED
    df["Basis"] = df["Basis"].fillna(BASIS_PRINTED)
    return df


def imputed_total(df: pd.DataFrame, country: str, basis: str = BASIS_IMPUTED) -> float:
    """5-yr imputed (or baseline) government $ for one country in a
    budget-series frame (0 when the frame was loaded without those rows)."""
    m = df[(df["Country"] == country) & (df.get("Basis") == basis)
           & (df["Investment area"] != "All areas combined")]
    return float(m["Amount"].sum())


def load_budget_tidy() -> pd.DataFrame:
    df = pd.read_csv(DATA / "budget_tidy.csv")
    for c in (FOOTNOTE_COL, FOOTNOTE_LOC_COL):
        if c in df.columns:
            df[c] = df[c].fillna("")
    return df


def load_programmatic() -> pd.DataFrame:
    df = pd.read_csv(DATA / "programmatic_tidy.csv")
    df["Year"] = df["Year"].astype(str)
    for c in (FOOTNOTE_COL, FOOTNOTE_LOC_COL):
        if c in df.columns:
            df[c] = df[c].fillna("")
    return df


def load_countries() -> pd.DataFrame:
    return pd.read_csv(DATA / "countries.csv")


def load_sources() -> pd.DataFrame:
    return pd.read_csv(DATA / "sources.csv")


def add_share(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'Share' = Amount / (USG + Government) for that Country/Area/Year.

    Years where the combined total is zero get Share = NA.
    """
    totals = (
        df.groupby(["Country", "Investment area", "Year"])["Amount"]
        .sum()
        .rename("Combined")
        .reset_index()
    )
    out = df.merge(totals, on=["Country", "Investment area", "Year"], how="left")
    out["Share"] = out["Amount"].where(out["Combined"] > 0) / out["Combined"]
    return out


def area_options(df: pd.DataFrame) -> list:
    present = set(df["Investment area"].unique())
    ordered = [a for a in AREA_ORDER if a in present]
    return ordered + sorted(present - set(ordered))


def five_year_totals(df: pd.DataFrame, area: str) -> pd.DataFrame:
    """5-year totals per country & funder for one investment area."""
    m = df[df["Investment area"] == area]
    tot = m.groupby(["Country", "Funder"])["Amount"].sum().reset_index()
    comb = tot.groupby("Country")["Amount"].sum().rename("Combined").reset_index()
    tot = tot.merge(comb, on="Country")
    tot["Share"] = tot["Amount"].where(tot["Combined"] > 0) / tot["Combined"]
    return tot


# Direction of improvement. The authority is the `Direction` column of
# programmatic_tidy.csv, populated once per row; the keyword heuristic below is
# only the fallback for frames that lack it (and the seed that populated it).
# Keywords alone cannot be trusted: "# patients with TB notified (i.e.,
# bacteriologically confirmed + clinically diagnosed)" trips "diagnos" and reads
# as lower-is-better, when rising notification is exactly the goal.
DIRECTION_COL = "Direction"
# Inequality printed on a target cell where the MoU states a bound rather than an
# exact figure. `Value` always carries the numeric bound so the series stays
# plottable; this column preserves what was printed (">", "<", "≥", "≤", "~"),
# and blank means the cell is exact.
QUALIFIER_COL = "Qualifier"
LOWER_LABEL = "Lower is better"
HIGHER_LABEL = "Higher is better"

# Indicators where a FALL is the improvement (deaths, mortality, new cases…).
# These get a zero-based y-axis so the decline reads in true proportion rather
# than being exaggerated by a zoomed axis.
LOWER_IS_BETTER_KEYWORDS = (
    "death", "mortality", "cases", "diagnos", "incidence", "prevalence",
    "transmission rate", "stockout", "product loss", "lead time",
    "test positivity",
)
# Higher-is-better indicators that would otherwise trip a keyword above.
# Non-polio AFP rate is a surveillance-SENSITIVITY measure: a higher rate means
# the system is detecting more suspected cases, which is the goal.
LOWER_IS_BETTER_EXCEPTIONS = ("non-polio afp",)


def is_lower_better(indicator: str) -> bool:
    """True when a decline in this indicator is the intended direction."""
    t = (indicator or "").lower()
    if any(k in t for k in LOWER_IS_BETTER_EXCEPTIONS):
        return False
    return any(k in t for k in LOWER_IS_BETTER_KEYWORDS)


def lower_is_better(sub: pd.DataFrame) -> bool:
    """Direction for one indicator's rows: the data column when present,
    otherwise the keyword heuristic on the indicator name."""
    if DIRECTION_COL in sub.columns:
        vals = sub[DIRECTION_COL].dropna()
        if len(vals):
            return bool((vals == LOWER_LABEL).all())
    return is_lower_better(sub["Indicator"].iat[0])


def md(text: str) -> str:
    """Neutralise characters Streamlit's markdown would typeset in prose:
    $ (paired -> LaTeX math, serif italics) and ~ (paired -> strikethrough).

    Uses HTML entities rather than backslash escapes: backslashes are only
    consumed in pure-markdown context and show up literally inside HTML blocks
    (footnotes, legend chips), whereas entities render as the plain character
    in every context and never trigger the math/strikethrough parser. Wrap
    every st.caption / st.markdown / help string that contains $ amounts."""
    return text.replace("$", "&#36;").replace("~", "&#126;")


def fmt_usd(v: float) -> str:
    if pd.isna(v):
        return "–"
    if abs(v) >= 1e9:
        return f"${v / 1e9:,.2f}bn"
    if abs(v) >= 1e6:
        return f"${v / 1e6:,.1f}M"
    if abs(v) >= 1e3:
        return f"${v / 1e3:,.0f}k"
    return f"${v:,.0f}"


# ---------------------------------------------------------------------------
# Footnotes printed in the MoU texts themselves — asterisk, dagger and "Note:"
# lines attached to the source funding tables — transcribed verbatim.
# Convention: every note applies across the full 2026–2030 line; `marked`
# lists the specific cells the MoU itself stars (kept as context and shown
# in captions). Row-level copies live in the "MoU footnote (verbatim)" /
# "MoU footnote location" columns of budget_tidy.csv and programmatic_tidy.csv.
FOOTNOTE_COL = "MoU footnote (verbatim)"
FOOTNOTE_LOC_COL = "MoU footnote location"

BUDGET_FOOTNOTES = [
    dict(Country="Mozambique", Area="Surveillance & outbreak response", Funder="USG",
         marked=[2027, 2029],
         text="*Includes funding for surveys discussed in Section 4.1.",
         src="§2.1.3 p.6 · asterisks on the 2027 & 2029 cells; §4.1 plans up to $35M of outcome surveys"),
    dict(Country="Mozambique", Area="Laboratory commodities", Funder="USG", marked=None,
         text="*Total Costs are representative of one year; these amounts may fluctuate "
              "yearly based on the actual need as determined in the annual quantification.",
         src="App.2 p.35 · on the 2026 quantification table that sets the recurring annual amount"),
    dict(Country="Mozambique", Area="Other commodities", Funder="USG", marked=None,
         text="*Total Costs are representative of one year; these amounts may fluctuate "
              "yearly based on the actual need as determined in the annual quantification.",
         src="App.2 p.35 · on the 2026 Other Commodities quantification table"),
    dict(Country="Mozambique", Area="Other commodities", Funder="USG", marked=None,
         text="$5,000,000 (reduced to $2,000,000 in FY27-FY30)",
         src="App.2 p.35 · printed inside the 'MCH – TBD' cell; explains part of the 2026→'27 step-down"),
    dict(Country="Mozambique", Area="Frontline healthcare workers", Funder="Government", marked=None,
         text="*The total additional cost to employ 4,893 front-line Healthcare workers "
              "over the five-year period is $46,973,106",
         src="App.1 p.34 · printed under the GoM new-support table"),
    dict(Country="Mozambique", Area="Frontline lab workers", Funder="Government", marked=None,
         text="*The total additional cost to employ 4,893 front-line Healthcare workers "
              "over the five-year period is $46,973,106",
         src="App.1 p.34 · printed under the GoM new-support table. 4,893 = 4,788 HCW + 105 "
             "lab FTEs exactly, so this printed total already pays the lab cohort — which is "
             "why the government lab line carries no separate imputed $"),
    dict(Country="Mozambique", Area="All areas combined", Funder="Government", marked=None,
         text="*Includes funding for additional front-line Healthcare workers",
         src="App.1 p.33 · asterisk on the 'Mozambique Government' column header"),
    dict(Country="Kenya", Area="All areas combined", Funder="USG", marked=None,
         text="*Includes U.S. Government cost of doing business and funding for audits.",
         src="App.1 p.32 · under the headline USG total; the charts plot the itemised subtotal, "
             "which excludes that margin"),
    dict(Country="Kenya", Area="Frontline healthcare workers", Funder="Government", marked=None,
         text="*Includes public health emergency responders, logisticians, data scientists, "
              "laboratorians etc.",
         src="§2.1.2.5 p.6 · on the 'Other Positions' row of the GoK FELTP salaries table"),
    dict(Country="Uganda", Area="Frontline healthcare workers", Funder="USG", marked=None,
         text="*The table includes all clinical and community health extension workers.",
         src="§2.4.2 p.13 · under the HRH FTE table"),
    dict(Country="Uganda", Area="Frontline healthcare workers", Funder="Government", marked=None,
         text="*The table includes all clinical and community health extension workers.",
         src="§2.4.2 p.13 · under the HRH FTE table"),
    dict(Country="Nigeria", Area="All areas combined", Funder="USG", marked=None,
         text="Note: The U.S. Government budget earmarked a 6% Management & Operations "
              "(M&O) allocation of $124,693,440",
         src="App.1 p.32 · under the co-funding summary; qualifies the USG column"),
    dict(Country="Rwanda", Area="Data systems", Funder="USG", marked=[2026],
         text="Note: The total support for digital systems is $4,027,316 in 2026. This "
              "currently includes funds from different accounts (HIV, Malaria, GHS, MCH&N).",
         src="§2.5.3 p.10 · the plotted $1.35M line item sits inside this larger cross-account total"),
    dict(Country="Rwanda", Area="Strategic assistance / investment", Funder="USG", marked=None,
         text="Note: The Strategic Investments budget assumes a 6% M&O deduction for "
              "U.S. Government operating costs.",
         src="§2.6.3 p.12 · under the funding plan table"),
    dict(Country="Côte d'Ivoire", Area="Frontline healthcare workers", Funder="Government", marked=None,
         text="Côte d'Ivoire Existing # FTEs Funded* — the asterisk is printed on this column "
              "header, but no matching footnote text appears anywhere in the document, "
              "appendices included (confirmed against the complete 29-page FOIA release)",
         src="§2.4.3 p.11 · orphan marker on the frontline-worker FTE table"),
    dict(Country="Côte d'Ivoire", Area="All areas combined", Funder="Government", marked=None,
         text="*This amount represents additional domestic health expenditure per year in "
              "the national budget, building off a baseline of actual expenses from the 2025 "
              "budget.",
         src="App.1 p.25 · on the \u201cCote d\u2019Ivoire Government*\u201d column of the "
             "co-funding summary; confirms that the $450M column is a domestic-expenditure "
             "pledge, which is why the charts exclude it"),
]
# Chart frames label government lines with GOV_LABEL — mirror that here once.
for _n in BUDGET_FOOTNOTES:
    if _n["Funder"] == "Government":
        _n["Funder"] = GOV_LABEL


def budget_footnotes(area=None, country=None, funders=None) -> list:
    """Printed MoU footnotes matching a chart selection (all filters optional)."""
    return [
        n for n in BUDGET_FOOTNOTES
        if (area is None or n["Area"] == area)
        and (country is None or n["Country"] == country)
        and (funders is None or n["Funder"] in funders)
    ]


def attach_budget_notes(df: pd.DataFrame, area: str) -> pd.DataFrame:
    """Add a 'MoU footnote' column (blank when none) for chart tooltips.

    Works on plotting frames with a Country column; respects Funder when present
    (frames aggregated across funders collect both funders' notes).
    """
    df = df.copy()
    if df.empty:
        df["MoU footnote"] = pd.Series(dtype=str)
        return df

    def note_for(row):
        notes = [
            n["text"] for n in BUDGET_FOOTNOTES
            if n["Area"] == area and n["Country"] == row["Country"]
            and ("Funder" not in row.index or n["Funder"] == row["Funder"])
        ]
        return " • ".join(dict.fromkeys(notes))

    df["MoU footnote"] = df.apply(note_for, axis=1)
    return df


def footnote_block(notes: list, size_px: int = 12) -> str:
    """Markdown/HTML block listing printed MoU footnotes (render with
    st.markdown(..., unsafe_allow_html=True))."""
    if not notes:
        return ""
    lines = []
    for n in notes:
        marked = (
            f" <i>(* printed on {' & '.join(str(y) for y in n['marked'])})</i>"
            if n.get("marked") else ""
        )
        lines.append(
            f"<div>* <b>{n['Country']}</b> — “{md(str(n['text']))}”{marked} "
            f"<span style='opacity:.75'>[{md(str(n['src']))}]</span></div>"
        )
    muted = palette()["muted"]
    return (
        f"<div style='font-size:{size_px}px;color:{muted};line-height:1.5;"
        "margin:2px 0 10px'><b>Footnotes printed in the MoU texts</b>"
        + "".join(lines) + "</div>"
    )


# ---------------------------------------------------------------------------
# Theming. The app ships light & dark themes (.streamlit/config.toml); with
# Streamlit's default "Use system setting" the active one follows the
# browser/OS colour-scheme preference. Colors Streamlit cannot restyle —
# explicit hexes in Altair specs and custom HTML — come from palette(), which
# reads the ACTIVE theme via st.context.theme, so they also honour a manual
# override in the app menu. Dark values validated with the dataviz palette
# checker against the dark surface (separation & contrast pass; the Uganda /
# "Other" grays are intentional neutrals whose identity is carried by
# legends and labels, not hue).
_DARK_COUNTRY = dict(zip(SOLID_COUNTRIES, _HUES_DARK))
_DARK_COUNTRY.update(dict(zip(DASHED_COUNTRIES, _HUES_DARK)))
_DARK_AREA = {
    "Laboratory commodities": "#3987e5",
    "Frontline healthcare workers": "#3fae3f",
    "Data systems": "#7c6ee6",
    "Other health sector co-investment": "#96948d",
}


def is_dark() -> bool:
    """True when the active Streamlit theme is dark (light on any failure,
    so this module stays importable without Streamlit)."""
    try:
        import streamlit as st

        return getattr(getattr(st.context, "theme", None), "type", "light") == "dark"
    except Exception:
        return False


def palette() -> dict:
    """Theme-following colors for explicit hexes in charts and custom HTML.

    Call once per script run (pages re-execute every rerun, so the result
    always matches the theme currently shown). Do NOT bake the result into
    module-level constants or st.cache_data — those outlive the rerun.
    """
    if is_dark():
        return {
            "dark": True,
            "ink": "#fafaf9", "muted": "#9d9b94", "surface": "#0d0d0d",
            "usg": "#3987e5", "gov": GOV_COLOR,
            "country": {c: {**COUNTRY_COLORS, **_DARK_COUNTRY}[c] for c in COUNTRY_ORDER},
            "country_dash": dict(COUNTRY_DASH),
            "country_order": list(COUNTRY_ORDER),
            "area": {**AREA_COLORS, **_DARK_AREA},
        }
    return {
        "dark": False,
        "ink": "#0b0b0b", "muted": "#898781", "surface": "#fcfcfb",
        "usg": USG_COLOR, "gov": GOV_COLOR,
        "country": dict(COUNTRY_COLORS),
        "country_dash": dict(COUNTRY_DASH),
        "country_order": list(COUNTRY_ORDER),
        "area": dict(AREA_COLORS),
    }
