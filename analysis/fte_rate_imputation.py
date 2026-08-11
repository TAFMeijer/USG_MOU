"""
Back-engineer government $ contributions for frontline lab workers & healthcare
workers from USG $/FTE rates — Cameroon pilot.

Method
------
The MoUs give FTE counts for both funders, but $ only for the USG side (in
Cameroon's case). We derive a $/FTE rate from the USG side and apply it to the
government FTE commitments.

Key empirical findings that shape the method (see Cameroon_FTE_rate_analysis.md):
1. USG $ line items are NOT unit-cost x FTE: every USG line item tracks the
   total USG glide path (-9.3%, -6.1%, -15.1%, -34.3% p.a.) almost exactly,
   while FTE targets fall on a different, steeper trajectory. So $/FTE is only
   a clean unit cost in 2026, the first/full-funding year.
2. Peer MoUs that DO print government-side $ and FTEs use flat nominal rates
   (Mozambique HCW ~$4.0k, Kenya HCW ~$3.3k, Kenya lab $12,548 — identical to
   Kenya's USG 2026 rate). No inflation adjustment is applied in any MoU.
=> Canonical scenario: flat 2026 USG $/FTE rate (scenario A below).

Usage:  python fte_rate_imputation.py [path/to/budget_tidy.csv]
Writes: cameroon_imputed_gov_hrh.csv (imputed rows, budget_tidy-compatible)
        fte_rates_all_countries.csv  (every $/FTE rate computable from the data)
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data" / "budget_tidy.csv"
YRS = ["2026", "2027", "2028", "2029", "2030"]
INFLATION = 0.03  # scenario B only

df = pd.read_csv(DATA, encoding="utf-8-sig")
df["Year"] = df["Year"].astype(str)


def cam_series(area, funder, unit, rowtype="Line item"):
    x = df[(df["Country"] == "Cameroon") & (df["Investment area"] == area)
           & (df["Funder"] == funder) & (df["Unit"] == unit)
           & (df["Row type"] == rowtype)]
    return x.set_index("Year")["Amount"].reindex(YRS).fillna(0)


# ---------------------------------------------------------------- rates table
li = df[df["Row type"].str.startswith("Line item")]
rate_rows = []
for (c, a, f), g in li.groupby(["Country", "Investment area", "Funder"]):
    usd = g[g["Unit"] == "USD"].groupby("Year")["Amount"].sum()
    fte = g[g["Unit"] == "FTEs"].groupby("Year")["Amount"].sum()
    for y in usd.index.intersection(fte.index):
        if fte[y] > 0 and usd[y] > 0:
            rate_rows.append({"Country": c, "Investment area": a, "Funder": f,
                              "Year": y, "USD": usd[y], "FTEs": fte[y],
                              "USD_per_FTE": round(usd[y] / fte[y], 2)})
rates = pd.DataFrame(rate_rows).sort_values(["Country", "Investment area", "Funder", "Year"])
rates.to_csv(HERE / "fte_rates_all_countries.csv", index=False)

# ------------------------------------------------------------ Cameroon inputs
usg_lab_usd = cam_series("Frontline lab workers", "USG", "USD")
usg_lab_fte = cam_series("Frontline lab workers", "USG", "FTEs")
usg_hcw_usd = cam_series("Frontline healthcare workers", "USG", "USD")
usg_hcw_fte = cam_series("Frontline healthcare workers", "USG", "FTEs")
gov_lab_fte = cam_series("Frontline lab workers", "Government", "FTEs")
gov_hcw_fte = cam_series("Frontline healthcare workers", "Government", "FTEs")

R26_LAB = usg_lab_usd["2026"] / usg_lab_fte["2026"]   # 6,185.90
R26_HCW = usg_hcw_usd["2026"] / usg_hcw_fte["2026"]   # 4,399.68
BLEND_LAB = usg_lab_usd.sum() / usg_lab_fte.sum()     # 6,993.58
BLEND_HCW = usg_hcw_usd.sum() / usg_hcw_fte.sum()     # 4,893.71
infl = pd.Series([(1 + INFLATION) ** i for i in range(5)], index=YRS)

SCENARIOS = {
    "A: flat 2026 USG rate (canonical)": (gov_lab_fte * R26_LAB, gov_hcw_fte * R26_HCW),
    "B: 2026 USG rate +3%/yr": (gov_lab_fte * R26_LAB * infl, gov_hcw_fte * R26_HCW * infl),
    "C: blended 5-yr USG rate": (gov_lab_fte * BLEND_LAB, gov_hcw_fte * BLEND_HCW),
    "D: peer-government rate (Moz $4.0k HCW)": (gov_lab_fte * R26_LAB, gov_hcw_fte * 4000.0),
}

# ------------------------------------------------------- imputed rows (A) out
out = []
for area, fte_s, rate, rate_lbl in [
    ("Frontline lab workers", gov_lab_fte, R26_LAB, "USG 2026 lab rate $6,185.90/FTE"),
    ("Frontline healthcare workers", gov_hcw_fte, R26_HCW, "USG 2026 HCW rate $4,399.68/FTE"),
]:
    for y in YRS:
        out.append({
            "Country": "Cameroon", "Investment area": area, "Year": y,
            "Funder": "Government", "Amount": round(fte_s[y] * rate, 0),
            "Unit": "USD", "Row type": "Imputed (derived - not printed in MoU)",
            "Category (as printed in MoU)": "",
            "Source note": f"Imputed: {int(fte_s[y])} Gov FTEs x {rate_lbl}; "
                           "flat nominal, consistent with Moz/Kenya gov-side rates",
            "Source (MoU PDF)": "Cameroon_MoU.pdf (FTEs); rate derived",
        })
imputed = pd.DataFrame(out)
imputed.to_csv(HERE / "cameroon_imputed_gov_hrh.csv", index=False)

# ------------------------------------------------------------------- summary
gov_labcom = cam_series("Laboratory commodities", "Government", "USD")
gov_othcom = cam_series("Other commodities", "Government", "USD")
coinv = cam_series("Commodities & HRH co-investment", "Government", "USD",
                   "Aggregate co-investment (overlaps itemised rows - do not sum)")
dhe = cam_series("Domestic health expenditure increase", "Government", "USD",
                 "Alternative measure (do not sum)")

print(f"{'Scenario':<42}{'HRH imputed':>14}{'+new commod.':>14}"
      f"{'% of $72.6M':>12}{'% of $450M':>12}")
for name, (lab, hcw) in SCENARIOS.items():
    hrh = (lab + hcw).sum()
    item = hrh + gov_labcom.sum() + gov_othcom.sum()
    print(f"{name:<42}{hrh:>14,.0f}{item:>14,.0f}"
          f"{100 * item / coinv.sum():>11.0f}%{100 * item / dhe.sum():>11.0f}%")
print("\nPrinted co-investment aggregate (5yr): ", f"{coinv.sum():,.0f}")
print("Domestic health expenditure increase (5yr):", f"{dhe.sum():,.0f}")
