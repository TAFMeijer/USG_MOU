"""
Merge the imputed government HRH $ (from fte_rate_imputation_all.py) into the
dashboard data files so the charts can show them:

  data/budget_tidy.csv    gains the imputed rows with
                          Row type = "Imputed (derived - not printed in MoU)" /
                          "Imputed baseline (pre-MoU - derived)", so the detail
                          tables carry full provenance in their Source note.
  data/budget_series.csv  gains the matching Government rows under
                          Basis = "Imputed from FTEs" / "Imputed baseline
                          (pre-MoU)", per investment area AND as "All areas
                          combined", so KPIs, small multiples and donuts agree.

Idempotent: re-running drops previously imputed rows from both files first.

Pipeline order — this script writes only the IMPUTED bases. The printed bases
are rebuilt from the tidy file by rebuild_budget_series.py, which preserves the
imputed rows this script wrote. So always run, in this order:

    python analysis/fte_rate_imputation_all.py
    python analysis/apply_imputation_to_dashboard.py
    python analysis/rebuild_budget_series.py
    python analysis/rebuild_explorer_data.py
    python analysis/validate_data.py

NOTE: this script used to also split the printed existing-government rows into
their own basis by holding each series' 2026 level flat and leaving the growth
above it under "Printed in MoU". rebuild_budget_series.py now assigns the WHOLE
existing row to the existing basis, so that split has been removed rather than
left to fight the rebuild.
"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

BASIS_PRINTED = "Printed in MoU"
BASIS_IMPUTED = "Imputed from FTEs"
BASIS_BASELINE = "Imputed baseline (pre-MoU)"
IMPUTED_ROW_TYPE = "Imputed (derived - not printed in MoU)"
BASELINE_ROW_TYPE = "Imputed baseline (pre-MoU - derived)"
COLS = ["Country", "Investment area", "Year", "Funder", "Amount"]

imp = pd.read_csv(HERE / "imputed_gov_hrh_all_countries.csv")
imp = imp[imp["Amount"] > 0].copy()
imp["Year"] = imp["Year"].astype(int)
base = pd.read_csv(HERE / "imputed_baseline_workforce.csv")
base = base[base["Amount"] > 0].copy()
base["Year"] = base["Year"].astype(int)


def with_all_areas(frame, basis):
    """Per-area rows plus the matching 'All areas combined' aggregate."""
    all_rows = (
        frame.groupby(["Country", "Year"], as_index=False)["Amount"].sum()
        .assign(**{"Investment area": "All areas combined", "Funder": "Government"})
    )
    out = pd.concat([frame[COLS], all_rows[COLS]], ignore_index=True)
    out["Basis"] = basis
    return out


# ---------------------------------------------------------------- series file
s = pd.read_csv(DATA / "budget_series.csv", encoding="utf-8-sig")
if "Basis" not in s.columns:
    s["Basis"] = BASIS_PRINTED
s["Basis"] = s["Basis"].fillna(BASIS_PRINTED)
s = s[~s["Basis"].isin([BASIS_IMPUTED, BASIS_BASELINE])]          # idempotency

out = pd.concat([s, with_all_areas(imp, BASIS_IMPUTED),
                 with_all_areas(base, BASIS_BASELINE)], ignore_index=True)
out = out.sort_values(["Country", "Investment area", "Funder", "Basis", "Year"])
out.to_csv(DATA / "budget_series.csv", index=False)
per_area = lambda f: f[f["Investment area"] != "All areas combined"]["Amount"].sum()
print(f"budget_series.csv: imputed ${per_area(imp):,.0f} + "
      f"baseline ${per_area(base):,.0f} across {out['Country'].nunique()} countries")

# ------------------------------------------------------------------ tidy file
t = pd.read_csv(DATA / "budget_tidy.csv", encoding="utf-8-sig")
t = t[~t["Row type"].isin([IMPUTED_ROW_TYPE, BASELINE_ROW_TYPE])]  # idempotency

adds = []
for frame, rowtype in [(imp, IMPUTED_ROW_TYPE), (base, BASELINE_ROW_TYPE)]:
    x = frame.copy()
    x["Unit"] = "USD"
    x["Row type"] = rowtype
    for col in t.columns:
        if col not in x.columns:
            x[col] = ""
    adds.append(x[t.columns])
tidy_new = pd.concat(adds, ignore_index=True)
pd.concat([t, tidy_new], ignore_index=True).to_csv(DATA / "budget_tidy.csv", index=False)
print(f"budget_tidy.csv: {len(t)} rows + {len(tidy_new)} imputed/baseline rows")
