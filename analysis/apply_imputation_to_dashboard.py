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
IMPUTED_ROW_TYPE = "Imputed (derived - not printed in MoU)"

imp = pd.read_csv(HERE / "imputed_gov_hrh_all_countries.csv")
imp = imp[imp["Amount"] > 0].copy()
imp["Year"] = imp["Year"].astype(int)

# ---------------------------------------------------------------- series file
s = pd.read_csv(DATA / "budget_series.csv", encoding="utf-8-sig")
if "Basis" not in s.columns:
    s["Basis"] = BASIS_PRINTED
s["Basis"] = s["Basis"].fillna(BASIS_PRINTED)
s = s[s["Basis"] != BASIS_IMPUTED]  # idempotency

area_rows = imp[["Country", "Investment area", "Year", "Funder", "Amount"]].copy()
all_rows = (
    imp.groupby(["Country", "Year"], as_index=False)["Amount"].sum()
    .assign(**{"Investment area": "All areas combined", "Funder": "Government"})
)
new = pd.concat([area_rows, all_rows[area_rows.columns]], ignore_index=True)
new["Basis"] = BASIS_IMPUTED

out = pd.concat([s, new], ignore_index=True)
out = out.sort_values(["Country", "Investment area", "Funder", "Basis", "Year"])
out.to_csv(DATA / "budget_series.csv", index=False)
print(f"budget_series.csv: {len(s)} printed + {len(new)} imputed rows "
      f"(imputed $ total {new[new['Investment area'] != 'All areas combined']['Amount'].sum():,.0f})")

# ------------------------------------------------------------------ tidy file
t = pd.read_csv(DATA / "budget_tidy.csv", encoding="utf-8-sig")
t = t[t["Row type"] != IMPUTED_ROW_TYPE]  # idempotency

tidy_new = imp.copy()
tidy_new["Unit"] = "USD"
tidy_new["Row type"] = IMPUTED_ROW_TYPE
for col in t.columns:
    if col not in tidy_new.columns:
        tidy_new[col] = ""
tidy_new = tidy_new[t.columns]

pd.concat([t, tidy_new], ignore_index=True).to_csv(DATA / "budget_tidy.csv", index=False)
print(f"budget_tidy.csv: {len(t)} rows + {len(tidy_new)} imputed rows")
