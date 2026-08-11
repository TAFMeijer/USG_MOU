"""
Merge the imputed government HRH $ (from fte_rate_imputation_all.py) into the
dashboard data files so the charts can show them:

  data/budget_series.csv  gains a `Basis` column ("Printed in MoU" /
                          "Imputed from FTEs") and imputed Government rows for
                          the affected areas + matching "All areas combined"
                          rows, so KPIs, small multiples and donuts all agree.
  data/budget_tidy.csv    gains the imputed rows with
                          Row type = "Imputed (derived - not printed in MoU)"
                          so the detail tables show full provenance.

Idempotent: re-running first drops previously imputed rows, then re-appends.
Run from the repo root or analysis/:  python analysis/apply_imputation_to_dashboard.py
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

imp = pd.read_csv(HERE / "imputed_gov_hrh_all_countries.csv")
imp = imp[imp["Amount"] > 0].copy()
imp["Year"] = imp["Year"].astype(int)
base = pd.read_csv(HERE / "imputed_baseline_workforce.csv")
base = base[base["Amount"] > 0].copy()
base["Year"] = base["Year"].astype(int)

# ---------------------------------------------------------------- series file
s = pd.read_csv(DATA / "budget_series.csv", encoding="utf-8-sig")
if "Basis" not in s.columns:
    s["Basis"] = BASIS_PRINTED
s["Basis"] = s["Basis"].fillna(BASIS_PRINTED)
s = s[~s["Basis"].isin([BASIS_IMPUTED, BASIS_BASELINE])]  # idempotency

COLS = ["Country", "Investment area", "Year", "Funder", "Amount"]


def with_all_areas(frame, basis):
    area_rows = frame[COLS].copy()
    all_rows = (
        frame.groupby(["Country", "Year"], as_index=False)["Amount"].sum()
        .assign(**{"Investment area": "All areas combined", "Funder": "Government"})
    )
    out = pd.concat([area_rows, all_rows[COLS]], ignore_index=True)
    out["Basis"] = basis
    return out


new = with_all_areas(imp, BASIS_IMPUTED)
new_base = with_all_areas(base, BASIS_BASELINE)

out = pd.concat([s, new, new_base], ignore_index=True)
out = out.sort_values(["Country", "Investment area", "Funder", "Basis", "Year"])
out.to_csv(DATA / "budget_series.csv", index=False)
print(f"budget_series.csv: {len(s)} printed + {len(new)} imputed + {len(new_base)} baseline rows "
      f"(imputed $ {new[new['Investment area'] != 'All areas combined']['Amount'].sum():,.0f}; "
      f"baseline $ {new_base[new_base['Investment area'] != 'All areas combined']['Amount'].sum():,.0f})")

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
