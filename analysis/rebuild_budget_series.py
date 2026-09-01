"""Rebuild data/budget_series.csv (the aggregated, safely-summable series that feeds every
budget chart) from data/budget_tidy.csv, preserving any imputed rows already present.

Summing rule: only rows whose Row type is a line item count, and only USD. Years are capped
at 2030 so Kenya's co-financing table, which uniquely runs to 2031, does not distort the
five-year comparisons. Each country/year/funder also gets an "All areas combined" row.

  python analysis/rebuild_budget_series.py
"""
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
PRINTED = "Printed in MoU"
EXISTING = "Printed in MoU (existing/pre-MoU)"
KEEP_BASES = {"Imputed from FTEs", "Imputed baseline (pre-MoU)"}
BASIS_OF = {
    "Line item": PRINTED,
    "Line item - outside headline total": PRINTED,
    "Line item - existing (excl. from headline total)": EXISTING,
}
COLS = ["Country", "Investment area", "Year", "Funder", "Amount", "Basis"]

b = pd.read_csv(DATA / "budget_tidy.csv")
b = b[(b["Unit"] == "USD") & (b["Row type"].isin(BASIS_OF)) & (b["Year"] <= 2030)].copy()
b["Basis"] = b["Row type"].map(BASIS_OF)

areas = b.groupby(["Country", "Investment area", "Year", "Funder", "Basis"],
                  as_index=False)["Amount"].sum()
allc = (areas.groupby(["Country", "Year", "Funder", "Basis"], as_index=False)["Amount"].sum()
             .assign(**{"Investment area": "All areas combined"}))
printed = pd.concat([areas[COLS], allc[COLS]], ignore_index=True)

old = pd.read_csv(DATA / "budget_series.csv", encoding="utf-8-sig")
kept = old[old["Basis"].isin(KEEP_BASES)][COLS] if "Basis" in old.columns else old.iloc[:0][COLS]

out = pd.concat([printed, kept], ignore_index=True)
out = out.sort_values(["Country", "Investment area", "Funder", "Basis", "Year"])
out.to_csv(DATA / "budget_series.csv", index=False)
print(f"budget_series.csv: {len(old)} -> {len(out)} rows "
      f"({len(printed)} printed, {len(kept)} imputed carried over); "
      f"{out['Country'].nunique()} countries")
