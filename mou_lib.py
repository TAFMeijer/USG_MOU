"""Shared data loading & transforms for the MoU dashboard.

Pure pandas — no Streamlit imports — so everything here is unit-testable.
All figures originate from the co-funding appendices of the 9 published
America First bilateral health MoU texts (see data/sources.csv).
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"

YEARS = [2026, 2027, 2028, 2029, 2030]

# Consistent colors across the dashboard
USG_COLOR = "#2a78d6"
GOV_COLOR = "#eb6834"
COUNTRY_COLORS = {
    "Cameroon": "#2a78d6",
    "Côte d'Ivoire": "#eb6834",
    "Ethiopia": "#1baf7a",
    "Kenya": "#eda100",
    "Liberia": "#e87ba4",
    "Mozambique": "#008300",
    "Nigeria": "#4a3aa7",
    "Rwanda": "#e34948",
    "Uganda": "#52514e",
}

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


def load_budget_series() -> pd.DataFrame:
    """Aggregated, safely summable series: Country x Investment area x Year x Funder."""
    df = pd.read_csv(DATA / "budget_series.csv")
    df["Funder"] = df["Funder"].replace({"Government": GOV_LABEL})
    return df


def load_budget_tidy() -> pd.DataFrame:
    return pd.read_csv(DATA / "budget_tidy.csv")


def load_programmatic() -> pd.DataFrame:
    df = pd.read_csv(DATA / "programmatic_tidy.csv")
    df["Year"] = df["Year"].astype(str)
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
