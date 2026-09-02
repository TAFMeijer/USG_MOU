"""
Government $ imputation for frontline lab workers & healthcare workers —
ALL nine MoU countries (generalisation of the Cameroon pilot).

v2 — NEW vs EXISTING correction
-------------------------------
The MoU FTE tables print a "New # FTEs Funded" and an "Existing # FTEs Funded"
column, where Existing is written from each year's own perspective:
    Existing_t = pre-MoU baseline + cumulative prior-year NEW absorptions.
A worker absorbed in year t is paid in every later year, so the government's
MoU-driven funding base each year is

    funded_t = New_t + (Existing_t - pre-MoU baseline)   (= cumulative new)

The tidy 'Line item' FTE rows hold the NEW column; the
'Line item - existing (excl. from headline total)' FTE rows hold the printed
EXISTING column (baseline = its 2026 value). Countries whose tidy series is
already the TOTAL-funded column (Ethiopia, Mozambique, Rwanda — verified
against the source tables) have no existing-FTE rows and are used as-is.
Pre-MoU baseline workforces (CIV: 39,800 HCW + 1,900 lab; Uganda: 2,199 lab)
are NOT imputed — they are baseline effort, not MoU co-financing.

Rate hierarchy per country x area (unchanged from v1):
  1. PRINTED   — government $ is in the MoU: use it, no imputation.
  2. OWN RATE  — in-country USG $/FTE rate (2026 unit rate, flat nominal).
  3. PEER RATE — median of printed/validated government-side rates.

Internal validations (MoUs that do this arithmetic themselves):
  . Ethiopia HCW: printed gov $ == (USG FTE drawdown) x $1,748.29 to the dollar.
  . Kenya lab:    printed gov rate $12,548 == USG 2026 rate.
  . Mozambique:   gov HCW priced at ~$4,000 marginal; lab $ decomposes exactly
                  into $165,200 fixed + $6,600/FTE (residual 0.0000).

Pre-MoU BASELINE workforces (the 2026 value of each printed Existing column)
are valued separately in imputed_baseline_workforce.csv — visible, filterable,
never mixed into the MoU co-financing totals. Baselines printed in the MoUs:
CIV 39,800 HCW + 1,900 lab; Uganda 51,213 HCW + 2,199 lab; Mozambique 38,462
HCW (App.3 cadres); Liberia 6,577 HCW + 538 lab. None printed elsewhere.

Usage:  python fte_rate_imputation_all.py [path/to/budget_tidy.csv]
Writes: imputed_gov_hrh_all_countries.csv  (imputed rows, tidy-compatible)
        gov_hrh_summary_by_country.csv     (printed + imputed + method + range)
        imputed_baseline_workforce.csv     (pre-MoU baseline $, per year)
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data" / "budget_tidy.csv"
YRS = ["2026", "2027", "2028", "2029", "2030", "2031"]
HCW, LAB = "Frontline healthcare workers", "Frontline lab workers"
EXISTING_ROW = "Line item - existing (excl. from headline total)"

df = pd.read_csv(DATA, encoding="utf-8-sig")
df["Year"] = df["Year"].astype(str)
li = df[df["Row type"] == "Line item"]


def get(country, area, funder, unit, frame=None):
    x = (li if frame is None else frame)
    x = x[(x["Country"] == country) & (x["Investment area"] == area)
          & (x["Funder"] == funder) & (x["Unit"] == unit)]
    return x.groupby("Year")["Amount"].sum().reindex(YRS).fillna(0)


def funded_ftes(country, area):
    """Government FTEs actually funded each year under the MoU (cumulative new).

    New column + printed Existing column (minus its 2026 pre-MoU baseline)
    where an existing-FTE series is recorded; otherwise the tidy series is the
    total-funded column already.
    """
    new = get(country, area, "Government", "FTEs")
    ex_rows = df[(df["Row type"] == EXISTING_ROW) & (df["Unit"] == "FTEs")]
    ex = get(country, area, "Government", "FTEs", frame=ex_rows)
    if ex.sum() == 0:
        return new  # tidy series is already total funded (Eth, Moz, Rwa)
    baseline = ex["2026"]
    return new + (ex - baseline).clip(lower=0)


# ---------------------------------------------------------------- peer rates
def gov_rate_median(country, area):
    usd, fte = get(country, area, "Government", "USD"), get(country, area, "Government", "FTEs")
    r = [usd[y] / fte[y] for y in YRS if fte[y] > 0 and usd[y] > 0]
    return pd.Series(r).median() if r else None

peer_hcw = {c: gov_rate_median(c, HCW) for c in ["Kenya", "Liberia", "Mozambique"]}
peer_hcw["Ethiopia"] = 14173411 / 8107  # printed gov $ / mirrored FTEs (see validations)
# Uganda's printed gov $ prices each year's NEW cohort of the NATIONAL HRH roll-up
# (incl. lab cadres): 19,177,200/5,355=3,581 . 21,177,200/5,897=3,591 .
# 19,677,200/5,449=3,611 . 16,970,200/2,678=6,337 (2030 mix shifts CHEW->clinical).
# Own rate = median of those four.
peer_hcw["Uganda"] = pd.Series(
    [19177200 / 5355, 21177200 / 5897, 19677200 / 5449, 16970200 / 2678]).median()
PEER_HCW_MEDIAN = pd.Series(peer_hcw).median()

peer_lab = {"Kenya": gov_rate_median("Kenya", LAB), "Liberia": gov_rate_median("Liberia", LAB),
            "Ethiopia (USG const.)": 433565 / 79, "Mozambique (marginal)": 6600.0,
            "Cameroon (USG 2026)": 1930000 / 312}
PEER_LAB_MEDIAN = pd.Series(peer_lab).median()

UGA_WAGE_FACTOR = peer_hcw["Uganda"] / PEER_HCW_MEDIAN

# ------------------------------------------------------------- imputation set
PLANS = [
    ("Cameroon", HCW, 22170000 / 5039, 4000.0, 4893.71,
     "own USG 2026 rate (envelope caveat); cumulative new+existing FTEs", "medium"),
    ("Cameroon", LAB, 1930000 / 312, 1930000 / 312, 6993.58,
     "own USG 2026 rate (envelope caveat); cumulative new+existing FTEs", "medium"),
    ("Ethiopia", LAB, 433565 / 79, 433565 / 79, 219527 / 39,
     "own USG rate, constant across years", "high"),
    ("Mozambique", LAB, 6600.0, 6600.0, 858200 / 105,
     "own USG marginal rate (exact fixed+marginal fit)", "high"),
    ("Rwanda", HCW, 4272578 / 2734, 4272578 / 2734, 16807601 / 6609,
     "own USG 2026 rate (App.1 $ vs Sec FTEs misaligned)", "low"),
    ("Rwanda", LAB, 780319 / 289, 780319 / 289, 3704466 / 614,
     "own USG 2026 rate (App.1 $ vs Sec FTEs misaligned)", "low"),
    # CONTINUATION mode: Uganda's printed $ prices each year's NEW cohort only —
    # absorbed cohorts move into the Existing column unpriced. Impute the
    # continued salaries of previously absorbed cohorts (funded minus new).
    ("Uganda", HCW, None, None, None,
     "CONTINUATION of absorbed cohorts (printed $ covers new cohorts only); own rate", "medium"),
    ("Uganda", LAB, None, None, None,
     "CONTINUATION of absorbed lab cohorts (new-year costs sit in the printed HRH $)", "low"),
    # CIV moved from peer rates to its OWN printed rates: App.1 (pp.25-26 of the
    # FOIA release) prices the USG's frontline workers, which the earlier
    # 24-page scan never showed. HCW $13.4M / 5,556 CORE FTEs = $2,411.81
    # (2027-28 give $2,666.67 / $2,521.74; the seasonal CHW column is excluded,
    # and 2029-30 print $ against 0 core FTEs so they yield no rate at all);
    # lab $1.0M / 65 = $15,384.62 (2027-28: $15,555.56 / $16,000.00). The
    # GOVERNMENT column still prices no health worker, so the imputation stands
    # and only its rate basis changes. Ranges bracket the own rate against the
    # peer-government median that used to be the central estimate.
    ("Côte d'Ivoire", HCW, 13400000 / 5556, 13400000 / 5556, PEER_HCW_MEDIAN,
     "own USG 2026 rate (App.1); cumulative new (39,800 baseline excl.)", "medium"),
    ("Côte d'Ivoire", LAB, 1000000 / 65, PEER_LAB_MEDIAN, 400000 / 25,
     "own USG 2026 rate (App.1); cumulative new (1,900 baseline excl.)", "medium"),
]
PEER_FILL = {
    ("Uganda", HCW): (peer_hcw["Uganda"], 19177200 / 5355, 77001800 / 19379),
    ("Uganda", LAB): (PEER_LAB_MEDIAN * UGA_WAGE_FACTOR, gov_rate_median("Liberia", LAB), PEER_LAB_MEDIAN),
}
CONTINUATION = {("Uganda", HCW), ("Uganda", LAB)}

imputed_rows, summary = [], []
for country, area, rate, lo, hi, method, conf in PLANS:
    if rate is None:
        rate, lo, hi = PEER_FILL[(country, area)]
    fte = funded_ftes(country, area)
    if (country, area) in CONTINUATION:
        fte = (fte - get(country, area, "Government", "FTEs")).clip(lower=0)
    else:
        assert get(country, area, "Government", "USD").sum() == 0, f"{country}/{area} has printed $"
    label = ("prior-year absorbed cohorts, continued" if (country, area) in CONTINUATION
             else "new + prior-year absorptions")
    for y in YRS:
        if fte[y] > 0:
            imputed_rows.append({
                "Country": country, "Investment area": area, "Year": y,
                "Funder": "Government", "Amount": round(fte[y] * rate, 0), "Unit": "USD",
                "Row type": "Imputed (derived - not printed in MoU)",
                "Source note": f"Imputed: {int(fte[y])} Gov FTEs ({label}) x "
                               f"${rate:,.2f}/FTE ({method}); confidence "
                               f"{conf}; range ${lo:,.0f}-${hi:,.0f}/FTE",
            })
    summary.append({"Country": country, "Area": area,
                    "Status": "IMPUTED (continuation)" if (country, area) in CONTINUATION else "IMPUTED",
                    "Gov FTE-years": fte.sum(), "Rate used": round(rate, 2),
                    "Gov $ (central)": round(fte.sum() * rate, 0),
                    "Gov $ (low)": round(fte.sum() * lo, 0),
                    "Gov $ (high)": round(fte.sum() * hi, 0),
                    "Method": method, "Confidence": conf})

# --------------------------------------------------- printed rows for summary
for country in sorted(df["Country"].unique()):
    for area in [HCW, LAB]:
        usd = get(country, area, "Government", "USD")
        if usd.sum() > 0:
            fte = get(country, area, "Government", "FTEs")
            summary.append({"Country": country, "Area": area, "Status": "printed in MoU",
                            "Gov FTE-years": fte.sum() or None, "Rate used": None,
                            "Gov $ (central)": usd.sum(), "Gov $ (low)": usd.sum(),
                            "Gov $ (high)": usd.sum(), "Method": "printed", "Confidence": "n/a"})

imp = pd.DataFrame(imputed_rows)
imp.to_csv(HERE / "imputed_gov_hrh_all_countries.csv", index=False)
s = pd.DataFrame(summary).sort_values(["Status", "Country", "Area"])
s.to_csv(HERE / "gov_hrh_summary_by_country.csv", index=False)

# --------------------------------------------- pre-MoU baseline workforce $
# Baseline stock = the 2026 value of each printed Existing column, held constant
# (growth in those columns is absorbed cohorts, already counted above / in
# printed $). Priced at own-country government rates where they exist.
BASELINES = [
    # (country, area, FTEs/yr, rate, rate label)
    ("Côte d'Ivoire", HCW, 39800, 13400000 / 5556, "own USG 2026 rate (App.1)"),
    ("Côte d'Ivoire", LAB, 1900, 1000000 / 65, "own USG 2026 rate (App.1)"),
    # Uganda national baseline 51,213 minus its 2,199 lab component (own rows)
    ("Uganda", HCW, 49014, peer_hcw["Uganda"], "own new-cohort rate (median $3,601)"),
    ("Uganda", LAB, 2199, PEER_LAB_MEDIAN * UGA_WAGE_FACTOR, "peer lab median x wage factor"),
    ("Mozambique", HCW, 38462, peer_hcw["Mozambique"], "own printed gov HCW rate"),
    ("Liberia", HCW, 6577, peer_hcw["Liberia"], "own printed gov HCW rate"),
    ("Liberia", LAB, 538, gov_rate_median("Liberia", LAB), "own printed gov lab rate"),
]
base_rows = []
for country, area, ftes, rate, lbl in BASELINES:
    for y in YRS[:5]:
        base_rows.append({
            "Country": country, "Investment area": area, "Year": y,
            "Funder": "Government", "Amount": round(ftes * rate, 0), "Unit": "USD",
            "Row type": "Imputed baseline (pre-MoU - derived)",
            "Source note": f"Pre-MoU baseline workforce: {ftes:,} existing FTEs "
                           f"(2026 value of the printed Existing column) x ${rate:,.2f}/FTE "
                           f"({lbl}); baseline effort, NOT MoU co-financing",
        })
baseline = pd.DataFrame(base_rows)
baseline.to_csv(HERE / "imputed_baseline_workforce.csv", index=False)

pd.options.display.float_format = "{:,.0f}".format
print("Peer gov HCW rates:", {k: round(v) for k, v in peer_hcw.items()},
      "-> median", round(PEER_HCW_MEDIAN))
print("Peer lab rates:    ", {k: round(v) for k, v in peer_lab.items()},
      "-> median", round(PEER_LAB_MEDIAN))
print()
print(s.to_string(index=False))
print()
imp_mask = s["Status"].str.startswith("IMPUTED")
own = s[imp_mask & s["Confidence"].isin(["high", "medium"])]["Gov $ (central)"].sum()
low = s[imp_mask & (s["Confidence"] == "low")]["Gov $ (central)"].sum()
prt = s[s["Status"] == "printed in MoU"]["Gov $ (central)"].sum()
print(f"Printed gov HRH $ across MoUs:      {prt:>15,.0f}")
print(f"Imputed, high/med confidence:       {own:>15,.0f}")
print(f"Imputed, low confidence:            {low:>15,.0f}")
print(f"TOTAL government HRH commitment:    {prt + own + low:>15,.0f}")
print(f"Pre-MoU baseline workforce (sep.):  {baseline['Amount'].sum():>15,.0f}")
print("\nBaseline by country/area (5-yr):")
print(baseline.groupby(["Country", "Investment area"])["Amount"].sum().to_string())
