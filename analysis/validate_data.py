"""Consistency checks over data/ — run before any commit that touches it.

    python3 analysis/validate_data.py

Each check encodes an invariant verified by hand against the MoU PDFs, so a
failure means either a transcription slip or a deliberate convention change that
also needs its documentation updated. Prints one line per check; exits non-zero
if any fails.

Run it last in the data pipeline:
    fte_rate_imputation_all.py -> apply_imputation_to_dashboard.py
    -> rebuild_budget_series.py -> rebuild_explorer_data.py -> validate_data.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))
import mou_lib as lib  # noqa: E402

AGGREGATE = "All areas combined"
# Row types rebuild_budget_series.py aggregates, and the basis each maps to.
BASIS_OF = {
    "Line item": lib.BASIS_PRINTED,
    "Line item - outside headline total": lib.BASIS_PRINTED,
    "Line item - existing (excl. from headline total)": lib.BASIS_PRINTED_EXISTING,
}
SERIES_YEARS = set(lib.YEARS)          # the series is capped at 2030
TIDY_YEARS = SERIES_YEARS | {2031}     # Kenya alone carries a 2031 column

failures = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def approx(a, b, tol=1.0):
    return abs(a - b) <= tol


tidy = pd.read_csv(DATA / "budget_tidy.csv")
series = pd.read_csv(DATA / "budget_series.csv")
prog = pd.read_csv(DATA / "programmatic_tidy.csv", encoding="utf-8-sig")
countries = pd.read_csv(DATA / "countries.csv", encoding="utf-8-sig")

# ---------------------------------------------------------------- aggregates
key = ["Country", "Year", "Funder", "Basis"]
lhs = series[series["Investment area"] == AGGREGATE].groupby(key)["Amount"].sum()
rhs = series[series["Investment area"] != AGGREGATE].groupby(key)["Amount"].sum()
joined = pd.concat([lhs.rename("agg"), rhs.rename("parts")], axis=1).fillna(0)
bad = joined[(joined["agg"] - joined["parts"]).abs() > 1]
check('"All areas combined" == sum of its per-area rows', bad.empty,
      f"{len(bad)} groups differ, e.g. {bad.head(2).to_dict('index')}")

# ------------------------------------------------------ tidy -> printed series
sm = tidy[tidy["Row type"].isin(BASIS_OF) & (tidy["Unit"] == "USD")
          & tidy["Year"].isin(SERIES_YEARS)].copy()
sm["Basis"] = sm["Row type"].map(BASIS_OF)
rebuilt = sm.groupby(["Country", "Investment area", "Year", "Funder", "Basis"])["Amount"].sum()
printed = series[series["Basis"].isin(set(BASIS_OF.values()))
                 & (series["Investment area"] != AGGREGATE)]
got = printed.groupby(["Country", "Investment area", "Year", "Funder", "Basis"])["Amount"].sum()
diff = pd.concat([rebuilt.rename("tidy"), got.rename("series")], axis=1).fillna(0)
off = diff[(diff["tidy"] - diff["series"]).abs() > 1]
check("printed series reconciles to the tidy line items", off.empty,
      f"{len(off)} rows, e.g. {off.head(2).to_dict('index')} — run rebuild_budget_series.py")

# --------------------------------------------------------------- countries.csv
c = countries.dropna(subset=["Total agreement (USD)"])
sum_bad = c[(c["USG (USD)"] + c["Co-financing (USD)"]) != c["Total agreement (USD)"]]
check("countries.csv: USG + co-financing == total", sum_bad.empty, ", ".join(sum_bad["Country"]))
share_bad = c[((c["USG (USD)"] / c["Total agreement (USD)"]).round(3)
               - c["USG share"]).abs() > 5e-4]
check("countries.csv: share == USG / total", share_bad.empty, ", ".join(share_bad["Country"]))
public = set(countries.loc[countries["Full MoU text public"] == "Yes", "Country"])
check("every country with budget data is marked text-public",
      set(tidy["Country"]) <= public, str(set(tidy["Country"]) - public))
with_mou = set(countries.loc[countries["MoU USG (USD)"].notna(), "Country"])
check("every public text has its MoU-printed USG figure", public <= with_mou,
      str(public - with_mou))
check("no country without a public text carries MoU figures", with_mou <= public,
      str(with_mou - public))
noted = set(countries.loc[countries["MoU basis note"].astype(str).str.len() > 0, "Country"])
check("every MoU figure has a basis note", with_mou <= noted, str(with_mou - noted))

# ------------------------------------------------------------- explorer snapshot
before = [(ROOT / f).read_text(encoding="utf-8") for f in ("explorer.html", "docs/index.html")]
subprocess.run([sys.executable, str(ROOT / "analysis" / "rebuild_explorer_data.py")],
               check=True, capture_output=True)
after = [(ROOT / f).read_text(encoding="utf-8") for f in ("explorer.html", "docs/index.html")]
check("explorer.html + docs/index.html match budget_series", before == after,
      "regenerated in place — commit the change (rebuild_explorer_data.py)")
snap = json.loads(re.search(r"const DATA = (\{.*\});", after[0]).group(1))
check("explorer and docs copies are identical", after[0] == after[1])
check("explorer covers every country in the series",
      {r["country"] for r in snap["series"]} == set(series["Country"]))

# ------------------------------------------------- figures quoted on the methodology page
per_area = series[series["Investment area"] != AGGREGATE]


def by_basis(basis):
    return (per_area[per_area["Basis"] == basis].groupby("Country")["Amount"].sum()).to_dict()


imputed, baseline, existing = (by_basis(b) for b in
                               (lib.BASIS_IMPUTED, lib.BASIS_BASELINE, lib.BASIS_PRINTED_EXISTING))
quoted = [
    ("Cameroon imputed $27.7M", imputed["Cameroon"], 27.7e6, 0.05e6),
    ("Mozambique has no imputed lab $", imputed.get("Mozambique", 0.0), 0.0, 1.0),
    ("Uganda imputed $122.8M", imputed["Uganda"], 122.8e6, 0.05e6),
    ("CIV imputed $163.9M", imputed["Côte d'Ivoire"], 163.9e6, 0.05e6),
    ("Lesotho imputed $22.2M", imputed["Lesotho"], 22.2e6, 0.05e6),
    ("baseline workforce ~$3.20bn", sum(baseline.values()), 3.204e9, 5e6),
    ("Uganda baseline $951M", baseline["Uganda"], 951e6, 0.5e6),
    ("Mozambique baseline $877M (incl. 3,317 lab stock)", baseline["Mozambique"], 876.6e6, 0.5e6),
    ("CIV baseline $626M", baseline["Côte d'Ivoire"], 626e6, 0.5e6),
    ("Malawi baseline $287M", baseline["Malawi"], 287.4e6, 0.5e6),
    ("Burundi baseline $223M", baseline["Burundi"], 223.3e6, 0.5e6),
    ("Liberia baseline $156M", baseline["Liberia"], 156e6, 0.5e6),
    ("existing government $ ~$1.62bn", sum(existing.values()), 1.617e9, 5e6),
    ("Burundi has no existing basis (no pre-MoU base)",
     existing.get("Burundi", 0.0), 0.0, 1.0),
    ("Kenya existing $540M", existing["Kenya"], 540e6, 0.5e6),
    ("Botswana existing $362M", existing["Botswana"], 362e6, 0.5e6),
    ("Uganda existing $154M (flat 2026 base)", existing["Uganda"], 154.04e6, 0.5e6),
    ("CIV existing $219M", existing["Côte d'Ivoire"], 219e6, 0.5e6),
]
# Lesotho's imputed HRH $ must stay inside the MoU's own headline residual: the
# App.1 GoL column ($132,495,000) minus every itemised GoL row leaves $22,825,000
# unexplained over 2027-30, which is exactly the room the unpriced worker
# salaries occupy. If a data change pushes the imputation past it, something is
# double-counted.
LES_RESIDUAL = 132_495_000 - 8_315_000 - 101_356_000  # headline - lab - other commodities
quoted.append(("Lesotho imputed within the App.1 residual (cap-check)",
               imputed["Lesotho"], LES_RESIDUAL * 0.985, LES_RESIDUAL * 0.015))
for label, actual, want, tol in quoted:
    check(f"methodology figure: {label}", approx(actual, want, tol), f"data says {actual:,.0f}")

# ----------------------------------------------------------------- value domains
pct = prog.loc[prog["Value type"] == "Percentage", "Value"].dropna()
check("percentage values <= 100", bool((pct <= 100).all()), f"max {pct.max() if len(pct) else 0}")
check("budget years within the allowed set", not set(tidy["Year"]) - TIDY_YEARS,
      str(set(tidy["Year"]) - TIDY_YEARS))
check("series years within 2026-2030", not set(series["Year"]) - SERIES_YEARS,
      str(set(series["Year"]) - SERIES_YEARS))

page = (ROOT / "pages" / "3_Country_programmatic_view.py").read_text(encoding="utf-8")
section_order = set(eval(re.search(r"SECTION_ORDER = (\[[^\]]*\])", page).group(1)))
sections = set(prog["Metric type"])
check("every Metric type appears in SECTION_ORDER", sections <= section_order,
      str(sections - section_order))

areas = set(series["Investment area"]) - {AGGREGATE}
check("every plotted area has a colour", areas <= set(lib.AREA_COLORS), str(areas - set(lib.AREA_COLORS)))
check("every plotted area is in AREA_ORDER", areas <= set(lib.AREA_ORDER), str(areas - set(lib.AREA_ORDER)))
check("every country has a colour", set(series["Country"]) <= set(lib.COUNTRY_COLORS),
      str(set(series["Country"]) - set(lib.COUNTRY_COLORS)))

# ------------------------------------------------- programmatic direction & bounds
check("every indicator row carries a Direction",
      prog[lib.DIRECTION_COL].isin([lib.LOWER_LABEL, lib.HIGHER_LABEL]).all())
mixed = prog.groupby(["Country", "Indicator"])[lib.DIRECTION_COL].nunique() > 1
check("Direction is constant per country-indicator", not mixed.any(), str(list(mixed[mixed].index)))
QUALIFIERS = {">", "<", "≥", "≤", "~"}
q = prog[lib.QUALIFIER_COL].dropna()
check("Qualifier values are known symbols", set(q) <= QUALIFIERS, str(set(q) - QUALIFIERS))
check("no indicator row has a blank Value", bool(prog["Value"].notna().all()),
      "a printed bound belongs in Value + Qualifier, never only in a note")
dupes = prog.duplicated(["Country", "Indicator", "Year"]).sum()
check("no duplicate country/indicator/year rows", dupes == 0, f"{dupes} duplicates")

print()
if failures:
    print(f"{len(failures)} check(s) failed")
    sys.exit(1)
print("all checks passed")
