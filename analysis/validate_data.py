"""Consistency checks over data/ — run before any commit that touches it.

    python3 analysis/validate_data.py

Every check here encodes an invariant that was verified by hand against the MoU
PDFs, so a failure means either a transcription slip or a deliberate convention
change that also needs its documentation updated. Prints one line per check and
exits non-zero on the first failure group.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))
import mou_lib as lib  # noqa: E402

YEARS = set(lib.YEARS) | {2031}          # Kenya alone carries a 2031 column
AGGREGATE = "All areas combined"
SUMMABLE = ["Line item",
            "Line item - existing (excl. from headline total)",
            "Line item - outside headline total"]
PRINTED_BASES = [lib.BASIS_PRINTED, lib.BASIS_PRINTED_EXISTING]

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
per_area = series[series["Investment area"] != AGGREGATE]
agg = series[series["Investment area"] == AGGREGATE]
key = ["Country", "Year", "Funder", "Basis"]
lhs = agg.groupby(key)["Amount"].sum()
rhs = per_area.groupby(key)["Amount"].sum()
joined = pd.concat([lhs.rename("agg"), rhs.rename("parts")], axis=1).fillna(0)
bad = joined[(joined["agg"] - joined["parts"]).abs() > 1]
check('"All areas combined" == sum of its per-area rows', bad.empty,
      f"{len(bad)} groups differ, e.g. {bad.head(3).to_dict('index')}")

# ------------------------------------------------------- tidy -> series (printed)
# Convention: existing rows enter the printed series at their GROWTH above the
# held-flat 2026 level; the 2026 level itself is the separate existing basis.
sm = tidy[tidy["Row type"].isin(SUMMABLE) & (tidy["Unit"] == "USD")]
rebuilt = {}
for (c, a, f), g in sm.groupby(["Country", "Investment area", "Funder"]):
    by_year = g.groupby(["Row type", "Year"])["Amount"].sum().unstack(fill_value=0.0)
    printed = pd.Series(0.0, index=by_year.columns)
    for rt in SUMMABLE:
        if rt not in by_year.index:
            continue
        row = by_year.loc[rt]
        printed = printed + (row - row.get(2026, 0.0)).clip(lower=0) if rt.startswith(
            "Line item - existing") else printed + row
    for y, v in printed.items():
        rebuilt[(c, a, f, y)] = rebuilt.get((c, a, f, y), 0.0) + v
sp = series[(series["Basis"] == lib.BASIS_PRINTED)
            & (series["Investment area"] != AGGREGATE)]
mismatch = [(k, v, rebuilt.get(k, 0.0)) for k, v in
            zip(zip(sp["Country"], sp["Investment area"], sp["Funder"], sp["Year"]),
                sp["Amount"]) if not approx(v, rebuilt.get(k, 0.0))]
check("printed series reconciles to tidy line items", not mismatch,
      f"{len(mismatch)} rows, e.g. {mismatch[:3]}")

# --------------------------------------------------------------- countries.csv
c = countries.dropna(subset=["Total agreement (USD)"])
sum_bad = c[(c["USG (USD)"] + c["Co-financing (USD)"]) != c["Total agreement (USD)"]]
check("countries.csv: USG + co-financing == total", sum_bad.empty,
      ", ".join(sum_bad["Country"]))
share_bad = c[((c["USG (USD)"] / c["Total agreement (USD)"]).round(3)
               - c["USG share"]).abs() > 5e-4]
check("countries.csv: share == USG / total", share_bad.empty,
      ", ".join(share_bad["Country"]))

# ------------------------------------------------------------- explorer snapshot
sys.path.insert(0, str(ROOT / "analysis"))
import build_explorer_data as bex  # noqa: E402
import json  # noqa: E402

expected = bex.build()
for name in ("explorer.html", "docs/index.html"):
    text = (ROOT / name).read_text(encoding="utf-8")
    m = re.search(r"^const DATA = (\{.*\});$", text, re.M)
    got = json.loads(m.group(1)) if m else None
    check(f"{name} DATA matches budget_series", got == expected,
          "run analysis/build_explorer_data.py")

# ------------------------------------------------- methodology figures on page 4
page4 = (ROOT / "pages" / "4_Sources_and_methodology.py").read_text(encoding="utf-8")
imputed = {c: lib.imputed_total(series, c) for c in series["Country"].unique()}
baseline = {c: lib.imputed_total(series, c, lib.BASIS_BASELINE)
            for c in series["Country"].unique()}
existing = {c: lib.imputed_total(series, c, lib.BASIS_PRINTED_EXISTING)
            for c in series["Country"].unique()}
quoted = [
    ("Cameroon imputed $27.7M", imputed["Cameroon"], 27.7e6, 0.05e6),
    ("Uganda imputed $122.8M", imputed["Uganda"], 122.8e6, 0.05e6),
    ("CIV imputed $163.9M", imputed["Côte d'Ivoire"], 163.9e6, 0.05e6),
    ("Uganda baseline $951M", baseline["Uganda"], 951e6, 0.5e6),
    ("CIV baseline $626M", baseline["Côte d'Ivoire"], 626e6, 0.5e6),
    ("Mozambique baseline $767M", baseline["Mozambique"], 767e6, 0.5e6),
    ("Liberia baseline $156M", baseline["Liberia"], 156e6, 0.5e6),
    ("baseline workforce ~$2.50bn", sum(baseline.values()), 2.50e9, 5e6),
    ("existing commodity $ ~$889M (2026-30)", sum(existing.values()), 889e6, 1e6),
    ("Kenya existing $540M", existing["Kenya"], 540e6, 0.5e6),
    ("Uganda existing $154M", existing["Uganda"], 154e6, 0.5e6),
    ("CIV existing $130M", existing["Côte d'Ivoire"], 130e6, 0.5e6),
    ("Liberia existing $40M", existing["Liberia"], 40e6, 0.5e6),
    ("Mozambique existing $25M", existing["Mozambique"], 25e6, 0.5e6),
]
for label, actual, want, tol in quoted:
    check(f"methodology figure: {label}", approx(actual, want, tol), f"data says {actual:,.0f}")

# ----------------------------------------------------------------- value domains
pct = prog[prog["Value type"] == "Percentage"]["Value"].dropna()
check("percentage values <= 100", bool((pct <= 100).all()),
      f"max {pct.max() if len(pct) else 0}")
bad_years = set(tidy["Year"]) - YEARS
check("budget years within the allowed set", not bad_years, str(bad_years))

sections = set(pd.read_csv(DATA / "programmatic_tidy.csv",
                           encoding="utf-8-sig")["Metric type"])
spec = re.search(r"SECTION_ORDER = (\[[^\]]*\])",
                 (ROOT / "pages" / "2_Country_programmatic_view.py").read_text(encoding="utf-8"))
section_order = set(eval(spec.group(1)))  # literal list of strings
check("every Metric type appears in SECTION_ORDER", sections <= section_order,
      str(sections - section_order))

areas = set(series["Investment area"]) - {AGGREGATE}
check("every plotted area has a color", areas <= set(lib.AREA_COLORS),
      str(areas - set(lib.AREA_COLORS)))
check("every plotted area is in AREA_ORDER", areas <= set(lib.AREA_ORDER),
      str(areas - set(lib.AREA_ORDER)))

# --------------------------------------------------------- programmatic direction
check("every indicator row carries a Direction",
      prog[lib.DIRECTION_COL].isin([lib.LOWER_LABEL, lib.HIGHER_LABEL]).all())
QUALIFIERS = {">", "<", "≥", "≤", "~"}
q = prog[lib.QUALIFIER_COL].dropna()
check("Qualifier values are known symbols", set(q) <= QUALIFIERS,
      str(set(q) - QUALIFIERS))
check("qualified rows still carry a numeric Value",
      bool(prog.loc[prog[lib.QUALIFIER_COL].notna(), "Value"].notna().all()))
check("no indicator row has a blank Value", bool(prog["Value"].notna().all()),
      "a printed bound belongs in Value + Qualifier, not in the note")

mixed = (prog.groupby(["Country", "Indicator"])[lib.DIRECTION_COL].nunique() > 1)
check("Direction is constant per country-indicator", not mixed.any(),
      str(list(mixed[mixed].index)))

print()
if failures:
    print(f"{len(failures)} check(s) failed")
    sys.exit(1)
print("all checks passed")
