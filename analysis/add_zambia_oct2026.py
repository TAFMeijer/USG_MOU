# -*- coding: utf-8 -*-
"""Add Zambia (signed 8 Oct 2026) to the dashboard data, from the only public text:
Health GAP's "Final Draft MOU-Zambia" (47 pp., Google Docs export, Oct 2026).

  python3 analysis/add_zambia_oct2026.py

Writes Zambia's rows into data/budget_tidy.csv, data/programmatic_tidy.csv,
data/strategic_areas.csv, data/countries.csv (plus Vietnam, the other agreement the
KFF tracker added since the 34-country snapshot) and data/sources.csv. Idempotent:
every Zambia row is dropped and rewritten on each run. Then run the usual pipeline
(fte_rate_imputation_all -> impute_new_countries -> apply_imputation_to_dashboard ->
rebuild_budget_series -> rebuild_explorer_data -> validate_data).

The text is a FINAL DRAFT, not the executed copy: the signature block reads "SIGNED
at [INSERT CITY] on [DATE]" and Sec 6.5's notice names are "XX". It is used because
its amounts match the signed deal as announced (USG $1,516,265,000 = "more than $1.5
billion"; Table 5.1's cumulative domestic increase = the $975m pledge; App.1 Table 3's
new co-financing = the $154m Health Policy Watch reports). South Sudan stays excluded
because its only text is an April draft that predates the signed amounts.

Rows are written straight into the conventions the other 16 countries reached through
split_new_country_existing.py (no intermediate merged rows):
  * government New columns -> "Line item"; the 2026 Existing value held flat ->
    "Line item - existing (excl. from headline total)"; the Existing column's growth
    (prior-year totals rolled forward) -> "CONTINUATION" line items in the main band;
  * government FTEs: flat pre-MoU stock + cumulative new cohort;
  * the GRZ prints ONE worker $ line ("Healthcare Workers & CHW"), so the lab share is
    carved out pro-rata by the printed FTE mix (Uganda / Eswatini precedent).
Every figure is transcribed as printed; source inconsistencies are kept and flagged.
"""
from itertools import accumulate
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
C = "Zambia"
SRC = "https://healthgap.org/wp-content/uploads/2026/10/Final-Draft-MOU-Zambia.docx.pdf"
Y = [2026, 2027, 2028, 2029, 2030]
EXISTING_RT = "Line item - existing (excl. from headline total)"
SURV, LABC, LABW = ("Surveillance & outbreak response", "Laboratory commodities",
                    "Frontline lab workers")
OC, FHW, DS, SA = ("Other commodities", "Frontline healthcare workers", "Data systems",
                   "Strategic assistance / investment")
DRAFT = ("Text is Health GAP's FINAL DRAFT (signature block blank); amounts match the "
         "deal announced at signing on 8 Oct 2026. ")

# ---------------------------------------------------------------- printed tables
# App.1 Table 2 (pp.38-39): U.S. Government by line, as printed
USG = {
    SURV: [1963186, 1697072, 1487985, 1193301, 813535],
    LABC: [39050954, 29246148, 14681192, 12423672, 11100811],
    LABW: [4267600, 4267600, 2987320, 1493660, 298732],
    OC: [49821276, 37365957, 18682978, 15880531, 14292478],
    FHW: [63469730, 51873378, 43176114, 28111005, 18947714],
    DS: [31216156, 8172087, 4790620, 3295073, 3160765],
    SA: [116667318, 143991702, 180256739, 201301297, 147645794],
}
USG_FTE = {LABW: [175, 175, 123, 61, 12], FHW: [40422, 30860, 23636, 17197, 12614]}
USG_T2_TOTAL = [306456220, 276613944, 266062948, 263698539, 196259829]
USG_T1 = [348633000, 326133000, 320233000, 296633000, 224633000]       # App.1 Table 1
GOV_T1 = [345384526, 388802554, 421525013, 457701424, 493171963]
# Section tables (New / Estimated Existing / Total GRZ), identical to App.1 Tables 3/3.1
GOV = {
    SURV: ("Sec 2.1.3", "p.11", [0, 700000, 700000, 600000, 475020],
           [561581, 561581, 1261581, 1961581, 2561581],
           [561581, 1261581, 1961581, 2561581, 3036601]),
    LABC: ("Sec 2.2.3", "p.13", [0, 6494407, 7047485, 7466523, 8445587],
           [19230769, 19230769, 25725176, 32772661, 40239185],
           [19230769, 25725176, 32772661, 40239185, 48684772]),
    OC: ("Sec 2.3.3", "p.18", [0, 10455319, 11975458, 13802447, 13588053],
         [34610437, 34610437, 45065756, 57041214, 70843661],
         [34610437, 45065756, 57041214, 70843661, 84431714]),
    DS: ("Sec 2.5.3", "p.24", [0, 12806423, 37637, 1345563, 0],
         [1500000, 1500000, 14306423, 14344060, 15689623],
         [1500000, 14306423, 14344060, 15689623, 15689623]),
}
# App.1 Table 3 (new, p.39) and Table 3.1 (total, p.40): the only GRZ worker $ line
HRH_NEW = [5822718, 12961879, 12961879, 12961879, 12961879]
HRH_TOTAL = [289481739, 302443618, 315405496, 328367375, 341329253]
GOV_T3_TOTAL = [5822718, 43418028, 32722459, 36176412, 35470539]
GOV_T31_TOTAL = [345384526, 388802554, 421525012, 457701425, 493171963]
# FTE tables: lab Sec 2.2.3.2 (= App.3 Table 4), landscape App.3 Table 12
LAB_NEW, LAB_EXIST0 = [108, 195, 155, 70, 85], 2657
T12_NEW, T12_EXIST0 = [2500, 9375, 9375, 9375, 9375], 49079
HCW_NEW = [a - b for a, b in zip(T12_NEW, LAB_NEW)]          # 2,392 / 9,180 / ...
HCW_EXIST0 = T12_EXIST0 - LAB_EXIST0                          # 46,422

for (a, b, c_) in [(GOV[k][2], GOV[k][3], GOV[k][4]) for k in GOV]:
    assert all(abs(n + e - t) <= 1 for n, e, t in zip(a, b, c_)), (a, b, c_)
assert [sum(v[i] for v in USG.values()) for i in range(5)] == USG_T2_TOTAL
assert sum(USG_T1) == 1_516_265_000 and sum(GOV_T1) == 2_106_585_480

# ---------------------------------------------------------------- budget rows
budget = []


def b(area, funder, cat, vals, rowtype="Line item", unit="USD", note="", years=Y,
      fn="", fnloc=""):
    for y, v in zip(years, vals):
        budget.append({"Country": C, "Investment area": area, "Year": y, "Funder": funder,
                       "Amount": float(v), "Unit": unit, "Row type": rowtype,
                       "Category (as printed in MoU)": cat, "Source note": note,
                       "MoU footnote (verbatim)": fn, "MoU footnote location": fnloc,
                       "Source (MoU PDF)": SRC})


def money(v):
    return f"${v:,.0f}"


# --- U.S. Government, App.1 Table 2
ds_2026 = {"SmartCare Pro": 22758232, "DISA": 1926972, "e-LMIS integration": 483540,
           "e-IDSR": 109777, "National Health Data Warehouse": 450000, "WMS": 253992,
           "One National Reporting System": 511985, "track and trace": 3500000}
ds_term = [32193988, 7316919, 996195, 179701, 1950000, 584726, 1474457, 4375000]
USG_NOTES = {
    SURV: ("Surveillance & Outbreak Response ($)",
           "App.1 Table 2 p.38; identical to Sec 2.1.3 p.11. The GRZ takes over 10 "
           "provincial field epidemiologists and 30 District Surveillance Officers (Sec 2.1.2)"),
    LABC: ("Lab Commodities ($)",
           "App.1 Table 2 p.38; identical to Sec 2.2.3 Table 2.2.3.1 p.13. Sec 2.2.2: the "
           "USG historically funded $47,002,987 of lab commodities a year; the GRZ is to fund "
           "100% by the end of the MoU. 2026 breakdown in App.2 Table 1"),
    LABW: ("Frontline Lab Workers ($)",
           "App.1 Table 2 p.38: $24,386 per lab FTE in 2026-27 (4,267,600 / 175), four times "
           "the GRZ's own worker rate. Lab technologists only (App.3 Table 4)"),
    OC: ("Other Commodities ($)",
         "App.1 Table 2 p.39. 2029 and 2030 print $1 below Sec 2.3.3 ($15,880,532 / "
         "$14,292,479); App.1 values stored. Sec 2.3.2: historically $128 million of "
         "commodities a year. 2026 breakdown in App.2 Table 2"),
    FHW: ("Frontline Healthcare Workers ($)",
          "App.1 Table 2 p.39: $1,570 per FTE in 2026, the average over a workforce that is "
          "84% community workers (21,216 CHWs/CBVs + 12,876 seasonal malaria workers of "
          "40,422 FTEs); not a clinician's pay. The MoU prints no worker $ by cadre"),
    DS: ("Data Systems ($)",
         "App.1 Table 2 p.39; identical to Sec 2.5.3 p.24. 2026 by system: "
         + ", ".join(f"{k} {money(v)}" for k, v in ds_2026.items())
         + f" (sum {money(sum(ds_2026.values()))} against the {money(USG[DS][0])} line). "
         f"Term totals by system sum to {money(sum(ds_term))} against "
         f"{money(sum(USG[DS]))}. Sec 2.5.3 also supports 1,053 data personnel (halved in "
         "2030), outside the App.3 HRH counts. Full release is conditional on EMR data-entry "
         "rates of 90% (HIV) and 50% (other modules) by 2028"),
    SA: ("Strategic Assistance ($)",
         "App.1 Table 2 p.39; identical to Sec 2.6.3 p.27, which defines it as 'all costs not "
         "specified in Section 2.1.3, 2.2.3, 2.3.3, 2.4.3, and 2.5.3'. Peaks in 2029 "
         "($201.3m) while every other U.S. line tapers"),
}
FN = {
    SA: ("* This planned funding is dedicated to supporting strategic assistance that is "
         "expected to ensure long-term resilience and sustainability of the country\u2019s "
         "health systems for effective service delivery.",
         "Sec 2.6.3 p.27, beneath Table 2.6.3"),
    FHW: ("*Lab reductions: 30% in 2028, 50% in 2029, 80% in 2030. *CHW/Seasonal Worker "
          "reductions: 50% in 2029 and 2030. *All other cadres: 25% per year beginning 2027.",
          "App.3 p.44, beneath Table 3 (a chart with no legend or values)"),
}
FN_GOV_FHW = ("* Not part of the GRZ establishment",
              "App.3 Table 8 p.46, on the Community Based Volunteers / Community Health "
              "Worker table")
for area, (cat, note) in USG_NOTES.items():
    b(area, "USG", cat, USG[area], note=note, fn=FN.get(area, ("", ""))[0],
      fnloc=FN.get(area, ("", ""))[1])
b(LABW, "USG", "Frontline Lab Workers (# FTEs)", USG_FTE[LABW], unit="FTEs",
  note="App.1 Table 2 p.38; identical to Sec 2.2.3 Table 2.2.3.2 and App.3 Table 4 (lab "
       "technologists). Sec 2.2.2's text has the GRZ absorbing '123 ... in 2028, 61 ... in "
       "2029, and 12 ... in 2030': those are the USG-funded counts for those years, not the "
       "GRZ New column (155 / 70 / 85)")
b(FHW, "USG", "Frontline Healthcare Workers (# FTEs)", USG_FTE[FHW], unit="FTEs",
  fn=FN[FHW][0], fnloc=FN[FHW][1],
  note="App.1 Table 2 p.39 (printed in italics). Three different U.S. totals are printed: "
       "App.1 40,422 / 30,860 / 23,636 / 17,197 / 12,614 (the bar heights of App.3 Table 3, "
       "a chart with no legend or values); App.3 Table 12 37,756 / 29,817 / 23,113 / 17,084 / "
       "12,814 (incl. 175 lab); the App.3 cadre tables 5-11 sum to 36,461 / 28,354 / 21,515 / "
       "16,382 / 12,533. Sec 2.4.3 announces an FTE table but prints none. Sec 2.4.2 says CHW "
       "and seasonal-worker reductions start in 2029 at 50%, but Tables 8-9 cut 25% a year "
       "from 2027")
b("TOTAL", "USG", "TOTAL USG (App.1 Table 1 summary)", USG_T1,
  rowtype="Total / subtotal",
  note=DRAFT + "App.1 Table 1 p.38, term $1,516,265,000. Exceeds the itemised Table 2 total "
       "by $42.2m / $49.5m / $54.2m / $32.9m / $28.4m (12.1% / 15.2% / 16.9% / 11.1% / 12.6%; "
       "$207.2m over the term). No footnote explains the gap: it is not a flat 6% M&O wedge "
       "(that would be ~$91m). Sec 4.1's outcomes survey (up to $10m) and Sec 5.3's "
       "performance incentives sit outside the itemised table")
b("TOTAL", "USG", "App.1 detail-table Total $ (as printed)", USG_T2_TOTAL,
  rowtype="Appendix detail (do not sum)",
  note="App.1 Table 2 Total row p.39; foots exactly to its seven $ lines (term "
       f"{money(sum(USG_T2_TOTAL))})")

# --- U.S. Government App.2 (2026 commodity detail)
for area, items in [(LABC, {"HIV Rapid test kits": 4220320,
                            "Viral Load/EID/HPV/CD4 Reagents": 32271915,
                            "TB Reagents": 102403,
                            "Other Lab Reagents/Consumables": 2456316}),
                    (OC, {"ARVS including PrEP": 35507765, "ACTS, LLINS, RDTs": 11180000,
                          "Pharmaceuticals - OIs, TPT, IRS": 3133511})]:
    assert sum(items.values()) == USG[area][0]
    for k, v in items.items():
        b(area, "USG", f"App.2 2026: {k}", [v], rowtype="Appendix detail (do not sum)",
          years=[2026], note="App.2 p.41; the items foot exactly to the 2026 line")

# --- Government by area (Sec tables): NEW / flat EXISTING base / CONTINUATION
LABEL = {SURV: "surveillance & outbreak response", LABC: "lab commodities",
         OC: "commodities", DS: "data systems"}
for area, (sec, page, new, exist, total) in GOV.items():
    base = exist[0]
    lbl = LABEL[area]
    b(area, "Government", f"NEW GRZ: {lbl} ({sec})", new,
      note=f"{sec} New GRZ column, {page} (yearly increments), identical to App.1 Table 3. "
           "The printed Existing column rolls each prior year's Total forward "
           "(Existing_t = Total_t-1)")
    b(area, "Government", f"EXISTING GRZ: {lbl} ({sec})", [base] * 5, rowtype=EXISTING_RT,
      note="Pre-MoU base: the 2026 value of the Sec 'Estimated Existing GRZ' column, held "
           "flat - the level funded before the MoU; the column's growth (absorbed prior-year "
           "new commitments) is carried separately as a CONTINUATION line item in the main "
           "band")
    b(area, "Government", f"CONTINUATION GRZ: {lbl} ({sec} Existing above the 2026 base)",
      [e - base for e in exist],
      note="MoU-era continuation: the printed Existing column minus the flat 2026 pre-MoU "
           f"base of {money(base)}/yr - prior-year new commitments the MoU rolls into its "
           "Existing column; kept in the MAIN printed band (same rule as Lesotho, Sierra "
           "Leone, Madagascar, Burundi, Uganda)"
           + ("; the printed Totals for 2029-30 run $1 above base + cumulative new"
              if area == LABC else ""))

# --- Government workers: one printed $ line, lab share carved out by the FTE mix
hrh_exist = [t - n for t, n in zip(HRH_TOTAL, HRH_NEW)]       # Table 3.1 minus Table 3
hrh_base = hrh_exist[0]                                       # 283,659,021
hrh_cont = [e - hrh_base for e in hrh_exist]
lab_base_share = round(hrh_base * LAB_EXIST0 / T12_EXIST0)
lab_new_share = [round(d * l / n) for d, l, n in zip(HRH_NEW, LAB_NEW, T12_NEW)]
lab_cont_share = [0] + list(accumulate(lab_new_share))[:-1]
hcw_cont = [c_ - l for c_, l in zip(hrh_cont, lab_cont_share)]
assert all(abs(c_ - p) <= 2 for c_, p in zip(hrh_cont, [0] + list(accumulate(HRH_NEW))[:-1]))
SPLIT = ("Split pro-rata by the printed FTE mix: lab "
         f"{LAB_EXIST0:,} of the {T12_EXIST0:,} existing (App.3 Table 4 / Table 12) and "
         + " / ".join(f"{l} of {n:,}" for l, n in zip(LAB_NEW, T12_NEW))
         + " new (Sec 2.2.3.2 / App.3 Table 12); Uganda / Eswatini precedent, totals unchanged")
HRH_FN = ("App.1 Tables 3 and 3.1 print one GRZ worker line, 'Healthcare Workers & CHW ($)'; "
          "the MoU has no GRZ lab-worker $ line and Sec 2.4.3 prints no table. ")
b(FHW, "Government", "NEW GRZ: Healthcare Workers & CHW ($, App.1 Table 3) net of the lab share",
  [d - l for d, l in zip(HRH_NEW, lab_new_share)],
  note=HRH_FN + "Yearly new-cohort cost: $5,822,718 for the 2,500 hires of 2026 ($2,329 each), "
       "$12,961,879 a year for 9,375 from 2027 ($1,383 each: 3,125 permanent + 6,250 community "
       "workers, App.3 Table 1). " + SPLIT)
b(FHW, "Government",
  "EXISTING GRZ: Healthcare Workers & CHW ($, App.1 Table 3.1 minus Table 3) net of the lab share",
  [hrh_base - lab_base_share] * 5, rowtype=EXISTING_RT,
  note=HRH_FN + f"Pre-MoU workforce $: 2026 Total GRZ {money(HRH_TOTAL[0])} minus the "
       f"{money(HRH_NEW[0])} new cohort = {money(hrh_base)}, held flat ($5,780 per existing "
       "FTE over Table 12's 49,079). Printed, not imputed, so Zambia has no imputed-baseline "
       "rows (Botswana precedent). " + SPLIT)
b(FHW, "Government",
  "CONTINUATION GRZ: Healthcare Workers & CHW ($, prior-year cohorts) net of the lab share",
  hcw_cont,
  note=HRH_FN + "MoU-era continuation: Table 3.1 Total minus the flat base minus the year's "
       "new cohort = the prior years' cohorts kept on payroll (cumulative Table 3 increments, "
       "to within $2 of rounding); main printed band. " + SPLIT)
b(LABW, "Government", "NEW GRZ: frontline lab workers ($, share of the Healthcare Workers & CHW line)",
  lab_new_share,
  note="Lab share of each year's new-cohort $ on the printed 'Healthcare Workers & CHW' line. "
       + SPLIT + ". No per-cadre GRZ rate is printed")
b(LABW, "Government",
  "EXISTING GRZ: frontline lab workers ($, share of the Healthcare Workers & CHW line)",
  [lab_base_share] * 5, rowtype=EXISTING_RT,
  note=f"Lab share of the printed pre-MoU worker $ ({money(hrh_base)} x {LAB_EXIST0:,} / "
       f"{T12_EXIST0:,}), held flat. " + SPLIT)
b(LABW, "Government",
  "CONTINUATION GRZ: frontline lab workers ($, share of prior-year cohorts)", lab_cont_share,
  note="Lab share of the prior years' cohorts kept on payroll (cumulative). " + SPLIT)

# --- Government FTEs: flat pre-MoU stock + cumulative new cohort
NOTE_CUM = ("Cumulative new cohort (new + previously absorbed) per the uniform FTE "
            "convention; printed per-year New column: {printed}")
b(LABW, "Government", "Zambian Government New # FTEs Funded (Sec 2.2.3.2)",
  list(accumulate(LAB_NEW)), unit="FTEs",
  note=NOTE_CUM.format(printed=LAB_NEW) + " (Sec 2.2.3.2 = App.3 Table 4, lab technologists)")
b(LABW, "Government", "Existing # FTEs Funded (Sec 2.2.3.2)", [LAB_EXIST0] * 5,
  unit="FTEs", rowtype=EXISTING_RT,
  note="Pre-MoU stock held flat (2,657 lab technologists, Sec 2.2.3.2); the printed column "
       "rolls absorbed cohorts forward. Valued on the printed-existing worker line (its lab "
       "share)")
b(FHW, "Government", "Zambian Government New # FTEs (App.3 Table 12 net of lab)",
  list(accumulate(HCW_NEW)), unit="FTEs", fn=FN_GOV_FHW[0], fnloc=FN_GOV_FHW[1],
  note=NOTE_CUM.format(printed=HCW_NEW) + " (App.3 Table 12 New minus Table 4 lab New; "
       "the cadre tables 5-11 foot to it exactly). Includes 6,250 community-based volunteers "
       "a year from 2027 (Table 8, 'Not part of the GRZ establishment'), toward the 40,000 "
       "hires the MoU is conditioned on")
b(FHW, "Government", "Existing # FTEs Funded (App.3 Table 12 net of lab)", [HCW_EXIST0] * 5,
  unit="FTEs", rowtype=EXISTING_RT,
  note="Pre-MoU stock held flat: App.3 Table 12's 49,079 existing minus the 2,657 existing lab "
       "technologists. The cadre tables 5-11 sum to only 36,422 existing workers, exactly "
       "10,000 fewer; Table 12 is used as the landscape total. App.3 Table 2 lists 81,501 GRZ-"
       "funded posts in 2025 (151,594 approved). Valued on the printed-existing worker line")

# --- Government totals
b("TOTAL", "Government", "TOTAL GRZ (App.1 Table 1 summary)", GOV_T1,
  rowtype="Total / subtotal",
  note=DRAFT + "App.1 Table 1 p.38, term $2,106,585,480: Total GRZ funding, new + existing "
       "(it equals Table 3.1 to within $1 in 2028-29). The pre-existing worker $ alone is "
       f"{money(5 * hrh_base)} of it. New co-financing (Table 3) totals "
       f"{money(sum(GOV_T3_TOTAL))}")
b("TOTAL", "Government", "App.1 Table 3 Total (new GRZ support, as printed)", GOV_T3_TOTAL,
  rowtype="Appendix detail (do not sum)",
  note="App.1 Table 3 p.39, yearly increments; term "
       f"{money(sum(GOV_T3_TOTAL))} - the ~$154m co-financing reported at signing")
b("TOTAL", "Government", "App.1 Table 3.1 Total (total GRZ support, as printed)",
  GOV_T31_TOTAL, rowtype="Appendix detail (do not sum)",
  note="App.1 Table 3.1 p.40; foots exactly to its five lines. Prints 2027 Data Systems as "
       "'$14,306,42' (digit dropped; Sec 2.5.3 gives $14,306,423)")
b("Domestic health expenditure increase", "Government",
  "Increase in GRZ domestic health expenditure vs the 2026 estimate (Table 5.1, cumulative)",
  list(accumulate([0, 75e6, 125e6, 100e6, 100e6])), rowtype="Alternative measure (do not sum)",
  note="Sec 5.1 Table 5.1 pp.32-33: annual increases of $0 / $75m / $125m / $100m / $100m on "
       "an estimated $627,928,519, reaching $1,027,928,519 in 2030; the cumulative increases "
       "sum to $975m, the pledge announced at signing. The 2025 actual is to be agreed as the "
       "baseline; the USG cuts its funding 1:1 for any shortfall (most MoUs say 2:1), and Sec "
       "6.11 doubles the cut for missed co-investment or hiring")

# ---------------------------------------------------------------- indicators
prog = []
B24 = "Baseline Jan-Dec 2024."


def ind(area, name, mtype, vals, unit, vtype, direction, qual=None, note=None, loc=None,
        printed=None):
    """vals: Baseline + 2026-30; None = printed N/A (no row). qual: per-value symbols."""
    qual = qual or [None] * 6
    for yr, v, q in zip(["Baseline"] + Y, vals, qual):
        if v is None:
            continue
        prog.append({"Country": C, "Programmatic area": area, "Indicator": name,
                     "Metric type": mtype, "Year": yr, "Value": v, "Qualifier": q,
                     "Unit": unit, "Value type": vtype, "Direction": direction,
                     "Programmatic area (as printed)": printed or (
                         "Outcome Metrics" if mtype == "Outcome" else "Process Metrics"),
                     "Unit / source note": " ".join(x for x in [B24, note] if x),
                     "MoU footnote (verbatim)": None, "MoU footnote location": loc,
                     "Source (MoU PDF)": SRC})


HI, LO = "Higher is better", "Lower is better"
O, P = "Outcome", "Process"
L11, L12 = "Sec 1.1 Table 1.1, pp.2-4", "Sec 1.2 Table 1.2, pp.4-9"
for name in ["% People with HIV Who Know Their Status",
             "% People Who Know Their HIV Status on Treatment",
             "% People on Antiretroviral Treatment (ART) Who Are Virally Suppressed"]:
    ind("HIV/AIDS", name, O, [95] * 6, "%", "Percentage", HI, qual=[">"] * 6, loc=L11,
        note="Printed as '>95%' in every column, baseline included; stored as 95 with the "
             "'>' qualifier.")
ind("HIV/AIDS", "Vertical Transmission rate of HIV", O, [6, 5, 5, 4, 4, 3], "%", "Percentage",
    LO, loc=L11)
ind("Malaria", "# Malaria Case Fatality rate (In under five children)", O,
    [11, 9, 7, 5, 5, 5], "per 1,000", "Rate", LO, qual=[None] * 4 + ["<", "<"], loc=L11,
    note="Printed as 11/1,000 ... 5/1,000, then '<5/1,000' in 2029-30. A case fatality rate "
         "(deaths per 1,000 cases), not the death counts most MoUs use.")
ind("TB", "# TB Deaths per 100,000 population", O, [38, 36, 34, 31, 29, 27], "per 100,000",
    "Rate", LO, loc=L11)
ind("Polio", "# Polio cases (e.g. WPV and cVDPV)", O, [0] * 6, "count", "Absolute number", LO,
    loc=L11)
ind("Immunisation (measles)", "# Measles Cases", O, [4946, 2557, 1322, 684, 354, 183], "count",
    "Absolute number", LO, loc=L11,
    note="Each year roughly halves the last (-48% a year), the steepest measles path in any "
         "published MoU.")
ind("MCH", "Maternal Mortality Rate", O, [187, 159, 145, 131, 117, 103], "per 100,000", "Rate",
    LO, qual=[None] + ["<"] * 5, loc=L11,
    note="Targets printed as '<159/100,000' ... '<103/100,000'; no denominator wording "
         "(other MoUs use per 100,000 live births).")
ind("MCH", "Children Under 5 Mortality Rate", O, [42, 38, 34, 30, 27, 25], "per 1,000", "Rate",
    LO, qual=[None] + ["<"] * 5, loc=L11, note="Targets printed as '<38/1,000' ... '<25/1,000'.")
ind("MCH", "Antenatal attendance in the first trimester", O, [46, 48, 52, 56, 60, 65], "%",
    "Percentage", HI, loc=L11, note="Unique to Zambia among the published MoUs.")
ind("HIV/AIDS", "Cervical Cancer Screening for Women Living with HIV", O,
    [27, 30, 35, 40, 45, 50], "%", "Percentage", HI, loc=L11,
    note="Unique to Zambia among the published MoUs.")
ind("HIV/AIDS", "HIV Treatment coverage", P, [95] * 6, "%", "Percentage", HI, qual=[">"] * 6,
    loc=L12, note="Printed as '>95%' in every column; stored as 95 with the '>' qualifier.")
ind("HIV/AIDS", "# people on ART", P, [1314858, 1323463, 1328028, 1330804, 1333325, 1334033],
    "count", "Absolute number", HI, loc=L12)
ind("HIV/AIDS", "# new HIV diagnoses among infants (0-24 months)", P,
    [1246, 1125, 1012, 911, 820, 738], "count", "Absolute number", LO, loc=L12,
    note="Age band 0-24 months overlaps the next row's '18 months or older' by six months.")
ind("HIV/AIDS", "# new HIV diagnoses among children and adults (age 18 months or older)", P,
    [30400, 27360, 24624, 22162, 19945, 17951], "count", "Absolute number", LO, loc=L12,
    note="Baseline 30,400 equals the 2024 new-infection figure in the Preamble; each target is "
         "10% below the previous year.")
ind("HIV/AIDS", "# pregnant women living with HIV who receive ART", P,
    [55204, 43421, 41602, 39483, 37587, 35801], "count", "Absolute number", HI, loc=L12,
    note="A count, not the coverage % other MoUs use; the targets fall 21% in 2026 and then "
         "~4-5% a year, tracking fewer pregnancies with HIV rather than lower coverage.")
ind("HIV/AIDS", "% HIV exposed infants who receive ARV prophylaxis", P, [80, 85, 90, 95, 95, 95],
    "%", "Percentage", HI, loc=L12)
ind("Malaria", "% confirmed malaria cases that receive first-line antimalarial treatment (Facility)",
    P, [98] * 6, "%", "Percentage", HI, loc=L12)
ind("Malaria", "% confirmed malaria cases that receive first-line antimalarial treatment (Community)",
    P, [93, 95, 95, 95, 95, 95], "%", "Percentage", HI, loc=L12)
ind("Malaria", "# insecticide-treated nets distributed to populations at risk of malaria - Continuous Distribution",
    P, [753221, 1978756, 2046034, 2115599, 2187529, 2261905], "routine nets", "Absolute number",
    HI, loc=L12)
ind("Malaria", "# insecticide-treated nets distributed to populations at risk of malaria - Mass Distribution/Campaign",
    P, [None, 11162309, None, None, 12340014, None], "campaign nets", "Absolute number", HI,
    loc=L12, note="Campaign years only: baseline, 2027, 2028 and 2030 are printed 'N/A'.")
ind("TB", "# patients with TB notified (i.e., bacteriologically confirmed + clinically diagnosed)",
    P, [47839, 50000, 50000, 50000, 45000, 40000], "count", "Absolute number", HI, loc=L12,
    note="Targets fall to 45,000 and 40,000 in 2029-30.")
ind("TB", "% of patients with TB notified who completed treatment", P, [92, 90, 90, 90, 90, 90],
    "%", "Percentage", HI, loc=L12, note="Every target (90%) is below the 92% baseline.")
ind("Polio", "% surviving infants who received the first dose of the inactivated polio vaccine",
    P, [76.8, 80, 85, 90, 90, 95], "%", "Percentage", HI, loc=L12)
ind("Immunisation (measles)",
    "% of children aged 12-23 months who received second dose of measles-containing vaccine",
    P, [66.7, 75, 80, 85, 90, 95], "%", "Percentage", HI, loc=L12)
ind("MCH", "Median number of antenatal care visits for pregnant women", P, [4, 5, 5, 6, 6, 6],
    "visits", "Count (visits)", HI, loc=L12)
ind("Data systems & quality", "% accuracy of data fields assessed during the annual data audit",
    P, [95] * 6, "%", "Percentage", HI, qual=[">"] * 6, loc=L12,
    note="Printed as '>95%' in every column; stored as 95 with the '>' qualifier.")
for nm, d in [("Detects suspected infectious disease outbreaks with epidemic potential within X days of disease emergence", 7),
              ("Notifies the U.S. Government within X day(s) of detection of a confirmed infectious disease outbreak", 1),
              ("Completes relevant initial response actions within X days of notification", 7)]:
    prog.append({"Country": C, "Programmatic area": "GHS / outbreak response", "Indicator": nm,
                 "Metric type": "Outbreak response (7-1-7)", "Year": "Baseline", "Value": d,
                 "Qualifier": None, "Unit": "days", "Value type": "Days", "Direction": LO,
                 "Programmatic area (as printed)": "Infectious Disease Outbreak Response Metrics",
                 "Unit / source note": "Standing commitment for the whole term, not a yearly "
                 "target. Party named in the MOU: the GRZ (Government of the Republic of Zambia). "
                 "Notification also engages WHO, UNICEF and Africa CDC.",
                 "MoU footnote (verbatim)": None, "MoU footnote location": "Sec 1.3, p.9",
                 "Source (MoU PDF)": SRC})

# ---------------------------------------------------------------- strategic areas
AREAS = [
    "I. HIV Prevention, Care and Treatment (Including LEN scale-up, Ending Vertical "
    "Transmission of HIV, Cervical Cancer, and Noncommunicable Disease Integration)",
    "II. Malaria Vector Control and Case Management",
    "III. Tuberculosis Prevention, Case Finding, and Treatment",
    "IV. Global Health Security",
    "V. Cross-Cutting Systems Strengthening",
    "VI. Joint Planning",
]
strat = [{"Country": C, "Order": i + 1, "Item": a,
          "Note": ("Includes 'formalization and support of community health workers' and solar "
                   "power" if a.startswith("V.") else ""),
          "Source": "Sec 2.6.2 pp.26-27"} for i, a in enumerate(AREAS)]
strat.append({"Country": C, "Order": len(AREAS) + 1,
              "Item": "Strategic Assistance (Appendix 1 line)",
              "Price (as printed)": f"{money(sum(USG[SA]))} over FY26-30",
              **{f"FY{y - 2000}": float(v) for y, v in zip(Y, USG[SA])},
              "Note": "The six areas are unpriced; the single line is identical in Sec 2.6.3 "
                      "and App.1. Sec 2.6.4 adds two policy changes: de-medicalised PrEP "
                      "(incl. injectable PrEP by CHWs and private pharmacies) and formalising "
                      "the Community-Based Volunteer cadre under the National Community "
                      "Health Policy 2027-2031",
              "Source": "Sec 2.6.3 p.27; App.1 Table 2 p.39"})

# ---------------------------------------------------------------- write
t = pd.read_csv(DATA / "budget_tidy.csv")
t = t[t["Country"] != C]
t = pd.concat([t, pd.DataFrame(budget)[t.columns]], ignore_index=True)
t.to_csv(DATA / "budget_tidy.csv", index=False)



def append_rows(fname, rows):
    """Replace this country's rows by text, so the other countries' lines stay byte-identical."""
    path = DATA / fname
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    cols = pd.read_csv(path, nrows=0, encoding="utf-8-sig").columns
    kept = [ln for ln in lines if not ln.startswith(C + ",")]
    body = pd.DataFrame(rows).reindex(columns=cols).to_csv(index=False, header=False)
    path.write_text("".join(kept) + body, encoding="utf-8")


append_rows("programmatic_tidy.csv", prog)
append_rows("strategic_areas.csv", strat)

c = pd.read_csv(DATA / "countries.csv", encoding="utf-8-sig")
c = c[~c["Country"].isin([C, "Vietnam"])]
c = pd.concat([c, pd.DataFrame([
    {"Country": C, "Signed": "2026-10-08", "Total agreement (USD)": 2495000000.0,
     "USG (USD)": 1520000000.0, "Co-financing (USD)": 975000000.0, "USG share": 0.609,
     "MoU USG (USD)": sum(USG_T1), "MoU co-financing (USD)": sum(GOV_T1),
     "MoU basis note": (
         "App.1 Table 1 co-funding summary; both columns foot exactly. The government column "
         "is Total GRZ funding, new + existing (Table 3.1), of which $1.42bn is the pre-"
         f"existing worker $; new co-financing (Table 3) is {money(sum(GOV_T3_TOTAL))}. The "
         "$975m in the KFF tracker is Sec 5.1's cumulative increase in domestic health "
         "expenditure, a different measure. The USG summary ($1,516.3m) exceeds its own "
         "itemised Table 2 ($1,309.1m) by $207.2m, 11-17% a year, with no footnote; KFF's "
         "$1.52bn is the announced 'more than $1.5 billion'"),
     "Program areas": "HIV/AIDS; TB; Malaria; Polio; MCH; GHS", "Full MoU text public": "Yes",
     "MoU PDF URL": SRC, "Hosted by": "Health GAP",
     "Doc type": "MOU (US-Zambia); FINAL DRAFT, signature block blank, not the executed copy",
     "Note": (
         "Signed in Lusaka on 8 Oct 2026 (U.S. Chargé d'Affaires and Zambia's Minister of "
         "Finance) after a ten-month delay over a linked critical-minerals deal, now "
         "decoupled. The only public text is Health GAP's 'Final Draft': its amounts match "
         "the signed deal as announced (USG 'more than $1.5 billion' = $1,516,265,000; $975m "
         "domestic increase = Table 5.1; ~$154m new co-financing = App.1 Table 3). Reported "
         "changes at signing: provisions requiring specimens to be sent to the U.S. were "
         "removed and a separate data-sharing agreement was signed the same day; this draft's "
         "Sec 2.1.2 still plans 'a specimen sharing arrangement', so the executed text may "
         "differ there."),
     "Disclosure marker": "",
     "How the text became public": (
         "Not released by either government: a final pre-signature draft posted by Health GAP "
         "(Oct 2026) and linked from Public Citizen's table. No Case Act or FOIA marker"),
     "Specimen sharing agreement URL": "", "Data sharing agreement URL": ""},
    {"Country": "Vietnam", "Signed": "2026-09-11", "USG (USD)": 98750000.0,
     "Full MoU text public": "No",
     "Note": ("KFF tracker (8 Oct 2026): U.S. $98.75m announced; co-financing unclear - the "
              "State Department release projects annual health expenditure growing by ~$10.5bn "
              "over the term ($23.3bn to $33.8bn). Text not public")},
])], ignore_index=True)
c = c.sort_values("Country", key=lambda s_: s_.str.normalize("NFKD")).reset_index(drop=True)
for col in ["MoU USG (USD)", "MoU co-financing (USD)"]:
    c[col] = c[col].astype("Int64")
c.to_csv(DATA / "countries.csv", index=False)

src = pd.read_csv(DATA / "sources.csv")
src = src[~src["URL"].isin([SRC])]
src.loc[src["Source"].str.startswith("KFF"), "Notes"] = (
    "Amounts for all 36 countries (Zambia and Vietnam added 8 Oct 2026); program areas; dates")
src.loc[(src["Type"] == "Tracker") & src["Source"].str.startswith("Public Citizen"), "Notes"] = (
    "Hosts the public MoU texts + specimen-sharing agreements; table of all 36 agreements "
    "with Case Act (*) and FOIA (^) markers; links Health GAP's Zambia final draft")
src = pd.concat([src, pd.DataFrame([{
    "Type": "Source doc",
    "Source": "Health GAP - Final Draft MOU-Zambia (posted Oct 2026)",
    "URL": SRC,
    "Notes": ("Zambia full text: the final pre-signature draft (signature block blank). "
              "Agreement signed 8 Oct 2026; amounts match the announced deal")}])],
    ignore_index=True)
src.to_csv(DATA / "sources.csv", index=False)

print(f"budget_tidy.csv: +{len(budget)} Zambia rows; programmatic_tidy.csv: +{len(prog)}; "
      f"strategic_areas.csv: +{len(strat)}; countries.csv: {len(c)} agreements, "
      f"{(c['Full MoU text public'] == 'Yes').sum()} public texts")
print(f"GRZ worker $ base {money(hrh_base)}; lab share {money(lab_base_share)}/yr; "
      f"lab new {lab_new_share}")
