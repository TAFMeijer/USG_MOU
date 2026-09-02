"""Imputation for the 2026-wave FOIA countries, mirroring the original framework.

Two layers, appended to the same analysis CSVs that
apply_imputation_to_dashboard.py merges into the dashboard data:

1. imputed_gov_hrh_all_countries.csv  — LESOTHO ONLY. Its MoU is the only one of
   the 16 that prints government frontline-worker FTE commitments (Sec 2.2.3 lab,
   Sec 2.4.3 HCW) without pricing them anywhere: GoL HRH salaries sit inside the
   ~$22.8M unitemised residual of the App.1 GoL headline column. Priced at the
   country's own USG 2026 rates (App.1 $ ÷ FTEs):
     HCW  $8,333.33/FTE  = 11,125,000 / 1,335  (1,357 printed minus the 22 lab
                           workers the Sec 2.4.3 count folds in — audit F11)
     lab  $19,045.45/FTE = 419,000 / 22        (later years ~$19,000, near-flat)
   Gov FTEs priced = the Total column net of lab (absorbed workers stay funded —
   same convention as every other imputed country). Cap-check: the 2027-30 total
   (~$22.2M) sits within 3% of the MoU's own $22.8M unitemised GoL residual —
   validate_data.py enforces it.

2. imputed_baseline_workforce.csv — pre-MoU workforce stock for the new countries
   whose FTE tables print an existing 2026 workforce, valued flat for 2026-2030
   like the four originals. Rate = the government's own printed absorption cost
   (printed gov worker $ ÷ cumulative new FTEs, median across years; exact
   constant where the MoU prices workers at one rate). Stocks:
     Burundi   11,260 HCW (1,169 doctors + 10,091 nurses) + 1,344 lab
     Malawi    19,127 HCW + 639 lab
     Sierra Leone 12,554 HCW + 76 lab (the 76 = the all-government epidemiologists)
     Madagascar 5,769 HCW + 310 lab
     Eswatini  814 blended (754 HCW + 54 lab + 6 epi) — its $ lines aggregate
               cadres, so one blended rate; LOW confidence (yearly rates $2,000-
               $9,498)
   NOT valued (documented gaps): Botswana (its existing workforce $ is printed —
   split into the existing basis instead; valuing FTEs would double count),
   Lesotho (no pre-MoU stock tabulated — its Existing columns start at 0),
   Madagascar's 349 existing + 30/yr new epidemiologists (no derivable rate).

Idempotent: rewrites this script's countries' rows in both CSVs on each run.
Pipeline order: run AFTER fte_rate_imputation_all.py (which rewrites the CSVs
for the original six countries) and BEFORE apply_imputation_to_dashboard.py.
"""
from pathlib import Path
from statistics import median

import pandas as pd

HERE = Path(__file__).resolve().parent
IMPUTED_RT = "Imputed (derived - not printed in MoU)"
BASELINE_RT = "Imputed baseline (pre-MoU - derived)"
YEARS = [2026, 2027, 2028, 2029, 2030]
FHW = "Frontline healthcare workers"
LAB = "Frontline lab workers"


def rows(country, area, rowtype, amounts, note):
    return [dict(Country=country, **{"Investment area": area}, Year=y,
                 Funder="Government", Amount=round(a), Unit="USD",
                 **{"Row type": rowtype, "Source note": note})
            for y, a in zip(YEARS, amounts) if round(a) > 0]


# ---------------------------------------------------------------- 1. Lesotho
HCW_RATE = 11125000 / 1335          # own USG 2026, net of lab (audit F11)
LAB_RATE = 419000 / 22              # own USG 2026
GOV_TOTAL_FTES = [0, 213, 502, 823, 1043]   # Sec 2.4.3 Total column (incl. lab)
GOV_LAB_FTES = [0, 10, 12, 20, 22]          # Sec 2.2.3 Total column
imputed = (
    rows("Lesotho", FHW, IMPUTED_RT,
         [(f - l) * HCW_RATE for f, l in zip(GOV_TOTAL_FTES, GOV_LAB_FTES)],
         f"Imputed: Gov Total FTEs net of lab (Sec 2.4.3 minus Sec 2.2.3; absorbed "
         f"workers stay funded) x ${HCW_RATE:,.2f}/FTE (own USG 2026 rate, "
         f"11,125,000/1,335 - the printed 1,357 includes 22 lab workers); GoL never "
         f"prices these FTEs - they sit in the App.1 residual; confidence medium-high: "
         f"2027-30 imputed HRH total is within 3% of the MoU's own $22.8M unitemised "
         f"GoL residual")
    + rows("Lesotho", LAB, IMPUTED_RT,
           [f * LAB_RATE for f in GOV_LAB_FTES],
           f"Imputed: Gov Total lab FTEs (Sec 2.2.3) x ${LAB_RATE:,.2f}/FTE (own USG "
           f"2026 rate, 419,000/22; 2027-29 imply ~$19,000 - near-constant); "
           f"confidence medium-high (see HCW note for the residual cap-check)")
)

# ------------------------------------------------------- 2. pre-MoU baselines


def med_rate(dollars, ftes, label):
    rates = [d / f for d, f in zip(dollars, ftes) if f]
    r = median(rates)
    return r, (f"{label}: printed gov worker $ / cumulative new FTEs = "
               + ", ".join(f"${x:,.0f}" for x in sorted(rates)) + f"; median ${r:,.2f}")


BASELINES = []

# Burundi — App.1 gov $ over cumulative new FTEs (Sec 2.4.3 / 2.2.3)
r, prov = med_rate([23352, 78456, 122856, 152856], [6, 23, 34, 39], "own gov median")
BASELINES.append(("Burundi", FHW, 11260, r,
                  "11,260 existing FTEs (Sec 2.4.3: 1,169 doctors + 10,091 nurses; "
                  "CHWs 0 - volunteers)", prov, "medium"))
BASELINES.append(("Burundi", LAB, 1344, 1784.0,
                  "1,344 existing lab technicians (Sec 2.2.3)",
                  "own gov rate, exactly $1,784/FTE in all four priced years", "high"))
# Malawi
r, prov = med_rate([963958, 2121984, 3274011, 4429036], [351, 739, 1127, 1515],
                   "own gov median")
BASELINES.append(("Malawi", FHW, 19127, r,
                  "19,127 existing FTEs (Sec 2.4.3 Existing column, 2026)", prov,
                  "medium"))
r, prov = med_rate([365737, 562672, 1327325, 1693062], [99, 198, 380, 479],
                   "own gov median")
BASELINES.append(("Malawi", LAB, 639, r,
                  "639 existing lab FTEs (Sec 2.2.3 Existing column, 2026)", prov,
                  "medium"))
# Sierra Leone
r, prov = med_rate([945000, 2265000, 3945000, 5601000, 7731000],
                   [1000, 3250, 5625, 8000, 10100], "own gov median")
BASELINES.append(("Sierra Leone", FHW, 12554, r,
                  "12,554 existing FTEs (Sec 2.4.3 Existing column, 2026)", prov,
                  "medium"))
BASELINES.append(("Sierra Leone", LAB, 76, 2400.0,
                  "76 existing lab FTEs (Sec 2.2.3, 2026 - App.3 shows these are the "
                  "all-government epidemiologists)",
                  "own gov rate, exactly $2,400/FTE in every priced year", "high"))
# Madagascar
r, prov = med_rate([677641, 1755282, 2872923, 4034564], [2262, 4660, 7272, 9947],
                   "own gov median")
BASELINES.append(("Madagascar", FHW, 5769, r,
                  "5,769 existing FTEs (Sec 2.4.3 Existing column, 2026). Its 349 "
                  "existing + 30/yr new epidemiologists (App.3) are NOT valued - no "
                  "rate is derivable and the blended CHW-heavy rate would be "
                  "cadre-inappropriate", prov, "medium"))
BASELINES.append(("Madagascar", LAB, 310, 2314.0,
                  "310 existing lab FTEs (Sec 2.2.3 Existing column, 2026)",
                  "own gov rate, exactly $2,314/FTE in all four priced years", "high"))
# Mozambique — audit follow-up: Sec 2.2.3 prints 3,317 existing GoM lab FTEs
# (pre-MoU stock; the column rolls forward absorbed new cohorts, whose cost the
# printed $46,973,106 HCW total already pays). Valued at the own USG marginal
# rate: USG lab $ fit exactly $165,200 fixed + $6,600 x FTE in all four funded
# years; the marginal rate is used for the stock (the 2026 average, $8,173,
# would replicate the fixed component 3,317 times).
BASELINES.append(("Mozambique", LAB, 3317, 6600.0,
                  "3,317 existing lab FTEs (Sec 2.2.3 Existing column, 2026; "
                  "missed by the original App.3-cadre harvest)",
                  "own USG marginal rate $6,600/FTE (fixed+marginal fit, "
                  "exact in all four funded years)", "medium"))
# Eswatini — one blended stock: its gov $ line aggregates HCW + lab + epi
r, prov = med_rate([100000, 1614621, 2421932, 3229242], [50, 170, 360, 632],
                   "own gov blended median")
BASELINES.append(("Eswatini", FHW, 814, r,
                  "814 blended existing FTEs (754 HCW Sec 2.4.3 + 54 lab Sec 2.2.3 + "
                  "6 epi App.3); the GOKE $ line aggregates these cadres so one "
                  "blended rate is applied", prov,
                  "LOW - yearly implied rates span $2,000-$9,498"))

baseline = []
for country, area, stock, rate, stock_note, rate_note, conf in BASELINES:
    baseline += rows(country, area, BASELINE_RT, [stock * rate] * 5,
                     f"Pre-MoU baseline workforce: {stock_note} x ${rate:,.2f}/FTE "
                     f"({rate_note}); confidence {conf}; baseline effort, NOT MoU "
                     f"co-financing")

# ------------------------------------------------------------------- write
for fname, add, mine in [
    ("imputed_gov_hrh_all_countries.csv", imputed, {"Lesotho"}),
    ("imputed_baseline_workforce.csv", baseline,
     {(c, a) for c, a, *_ in BASELINES}),
]:
    df = pd.read_csv(HERE / fname)
    if isinstance(next(iter(mine)), tuple):  # idempotency by country-area pair
        df = df[~df.apply(lambda r: (r["Country"], r["Investment area"]) in mine,
                          axis=1)]
    else:
        df = df[~df["Country"].isin(mine)]
    out = pd.concat([df, pd.DataFrame(add)[df.columns]], ignore_index=True)
    out.to_csv(HERE / fname, index=False)
    tot = pd.DataFrame(add)["Amount"].sum()
    print(f"{fname}: +{len(add)} rows (${tot:,.0f}) for {sorted(mine)}")

les = pd.DataFrame(imputed)["Amount"].sum()
print(f"Lesotho imputed 2027-30 total ${les:,.0f} vs $22,825,000 App.1 residual "
      f"({les / 22825000:.1%})")
