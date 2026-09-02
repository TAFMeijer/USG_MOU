"""Split the 2026-wave countries' government funding into NEW vs EXISTING rows.

The seven FOIA-release MoUs were first ingested with their government commodity /
worker $ stored as single "Line item" rows — for some countries the appendix's
new-support values, for others (Botswana, Lesotho, Madagascar labs) the merged
totals including pre-existing funding. The nine original countries instead follow
the convention: the MoU's New column -> Row type "Line item" (Basis "Printed in
MoU"), the MoU's Existing column -> Row type "Line item - existing (excl. from
headline total)" (Basis "Printed in MoU (existing/pre-MoU)", removable with the
pre-MoU toggle). This script rewrites the affected rows so all 16 countries obey
that one convention, taking the section tables (which print both columns) as the
source. Where a country's own tables conflict, the Source note records it.

Botswana is the one country whose New column is yearly increments while its
appendix totals treat new commitments as persisting; its printed rows therefore
carry the CUMULATIVE new (matching Appendix 1), per the F6 audit finding.

Idempotent: keyed on the replacement Category strings — rerunning is a no-op.
Run before analysis/rebuild_budget_series.py.
"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
EXISTING_RT = "Line item - existing (excl. from headline total)"
YEARS = [2026, 2027, 2028, 2029, 2030]

t = pd.read_csv(DATA / "budget_tidy.csv")

# (country, area, category-to-drop or None, [(new_cat, new_vals, new_note),
#                                            (ex_cat, ex_vals, ex_note)], years)
OPS = [
    ("Lesotho", "Laboratory commodities",
     "Total Government of Lesotho lab commodity funding",
     ("NEW GoL: lab commodities (Sec 2.2.3)", [0, 150000, 150000, 300000, 490000],
      "Sec 2.2.3 New column; the printed Existing column rolls prior-year totals forward"),
     ("EXISTING GoL: lab commodities (Sec 2.2.3)",
      [1017000, 1167000, 1317000, 1617000, 2107000],
      "Sec 2.2.3 Existing column (pre-MoU base $1,017,000; later years absorb prior new "
      "commitments, per the whole-existing-row convention)"),
     YEARS),
    ("Lesotho", "Other commodities",
     "Total Government of Lesotho commodity funding (Sec 2.3.3)",
     ("NEW GoL: commodities (Sec 2.3.3)", [0, 1660000, 1826000, 2009000, 2210000],
      "Sec 2.3.3 New column. 2030 components sum to 24,307,000 vs the printed Total "
      "24,306,000 ($1k source misprint; components stored as printed)"),
     ("EXISTING GoL: commodities (Sec 2.3.3)",
      [16602000, 16602000, 18262000, 20088000, 22097000],
      "Sec 2.3.3 Existing column (pre-MoU base $16,602,000/yr - GoL already funds 70% of "
      "ARVs; later years absorb prior new commitments)"),
     YEARS),
    ("Eswatini", "Laboratory commodities", None,
     None,
     ("EXISTING GOKE: lab commodities (Sec 2.2.3)", [1980593] * 5,
      "Sec 2.2.3 Existing GOKE Funding column, flat $1,980,593/yr; previously not ingested"),
     YEARS),
    ("Eswatini", "Other commodities", None,
     None,
     ("EXISTING GOKE: ARVs (Sec 2.3.3)", [15657143] * 5,
      "Sec 2.3.3 Existing GOKE Funding column, flat $15,657,143/yr (ARVs only - the App.1 "
      "new column also carries logistics, whose existing funding the MoU does not print)"),
     YEARS),
    ("Eswatini", "Surveillance & outbreak response", None,
     None,
     ("EXISTING GOKE: Surveillance & Outbreak Response (Sec 2.1.3)", [1540990] * 5,
      "Sec 2.1.3 GOKE column baseline level held as printed ($1,540,990/yr; rises to "
      "$2,154,011 in 2029-30, i.e. a $613,021 increment, where App.1 prints the new "
      "component as $713,021 - the $100k conflict is in the source)"),
     YEARS),
    ("Malawi", "Laboratory commodities", None,
     None,
     ("EXISTING Government of Malawi: lab commodities (Sec 2.2.3)", [6628050] * 5,
      "Sec 2.2.3 Existing Malawi Funding column, flat $6,628,050/yr; previously not "
      "ingested. (Sec 2.3.3 prints existing OTHER-commodity funding as $0 - the "
      "$51,380,231 essential-drugs budget is other-donor money, footnoted as such)"),
     YEARS),
    ("Sierra Leone", "Laboratory commodities",
     "Sierra Leone Government: Lab Commodities ($)",
     ("NEW GoSL: lab commodities (Sec 2.2.3)", [10000, 50000, 75000, 75000, 75000],
      "Sec 2.2.3 New column. Supersedes the App.1 cumulative row (whose 2027 cell prints "
      "50,000 where the section arithmetic requires 60,000 - App.1 misprint)"),
     ("EXISTING GoSL: lab commodities (Sec 2.2.3)", [10000, 20000, 70000, 145000, 220000],
      "Sec 2.2.3 Existing column (pre-MoU base $10,000; rolls prior-year totals forward)"),
     YEARS),
    ("Sierra Leone", "Other commodities",
     "Sierra Leone Government: Other Commodities ($)",
     ("NEW GoSL: commodities (Sec 2.3.3)",
      [1378663, 1500000, 1500000, 1500000, 1627010],
      "Sec 2.3.3 New column. Yearly New+Existing reproduce the printed totals exactly; "
      "App.1's cumulative row differs in two digits (…633 vs …663; 7,505,643 vs the "
      "section-implied 7,505,673) - section stored as printed"),
     ("EXISTING GoSL: commodities (Sec 2.3.3)",
      [378662, 1757325, 3257325, 4757325, 6257325],
      "Sec 2.3.3 Existing column (pre-MoU base $378,662; rolls prior-year totals forward)"),
     YEARS),
    ("Madagascar", "Laboratory commodities",
     "Government of Madagascar: Lab Commodities ($)",
     ("NEW Government of Madagascar: lab commodities (Sec 2.2.3)", [0, 55928, 61521, 67676, 74441],
      "Sec 2.2.3 New column"),
     ("EXISTING Government of Madagascar: lab commodities (Sec 2.2.3)",
      [559284, 559284, 615212, 676733, 744407],
      "Sec 2.2.3 Existing column (pre-MoU base $559,284; rolls prior totals forward; the "
      "2030 cell prints 744,407 vs the 2029 Total's 744,409 - $2 source wobble)"),
     YEARS),
    ("Madagascar", "Other commodities",
     "Government of Madagascar: Other Commodities ($)",
     ("NEW Government of Madagascar: commodities (Sec 2.3.3)",
      [680358, 1886174, 2300045, 3042372, 3858931],
      "Sec 2.3.3 New column (yearly increments). Replaces the App.1 cumulative-new row; "
      "New+Existing reproduce the printed totals exactly"),
     ("EXISTING Government of Madagascar: commodities (Sec 2.3.3)",
      [9803311, 10483669, 12369843, 14669888, 17712260],
      "Sec 2.3.3 Existing column (pre-MoU base $9,803,311/yr, previously not ingested "
      "anywhere - App.1's government table excludes it; rolls prior totals forward)"),
     YEARS),
    ("Botswana", "Laboratory commodities",
     "Botswana Government: Lab Commodities",
     ("NEW Botswana Government: lab commodities (Sec 2.2.3, cumulative)",
      [0, 45740, 157534],
      "Sec 2.2.3 New increments 45,740 + 111,794 held cumulative (App.1 confirms new "
      "commitments persist - audit F6); year totals reproduce App.1 exactly"),
     ("EXISTING Botswana Government: lab commodities (Sec 2.2.3)", [22403902] * 3,
      "Sec 2.2.3 Existing column, flat $22,403,902/yr"),
     [2026, 2027, 2028]),
    ("Botswana", "Frontline lab workers",
     "Botswana Government: Frontline Lab Workers",
     ("NEW Botswana Government: frontline lab workers (Sec 2.2.3, cumulative)",
      [0, 21890, 44437],
      "Sec 2.2.3 New increments 21,890 + 22,547 held cumulative (audit F6); year totals "
      "reproduce App.1 exactly"),
     ("EXISTING Botswana Government: frontline lab workers (Sec 2.2.3)", [729675] * 3,
      "Sec 2.2.3 Existing column, flat $729,675/yr"),
     [2026, 2027, 2028]),
    ("Botswana", "Other commodities",
     "Botswana Government: Other Commodities",
     ("NEW Botswana Government: commodities (Sec 2.3.3)", [0, 0, 0],
      "Sec 2.3.3 New column: $0 in every year - Botswana's commodity co-financing is "
      "entirely pre-existing spending"),
     ("EXISTING Botswana Government: commodities (Sec 2.3.3)", [20467986] * 3,
      "Sec 2.3.3 Existing column, flat $20,467,986/yr"),
     [2026, 2027, 2028]),
    ("Botswana", "Frontline healthcare workers",
     "Botswana Government: Frontline Healthcare Workers",
     ("NEW Botswana Government: frontline healthcare workers (Sec 2.4.3, cumulative)",
      [0, 6421098, 12842195],
      "Sec 2.4.3 New increments 6,421,098 + 6,421,097 held cumulative (audit F6); year "
      "totals reproduce App.1 exactly. Sec 2.4.3's own 2028 total prints 94,205,363 vs "
      "components 94,195,362 ($10,001 source misprint)"),
     ("EXISTING Botswana Government: frontline healthcare workers (Sec 2.4.3)",
      [77053167] * 3,
      "Sec 2.4.3 Existing column, flat $77,053,167/yr - the bulk of Botswana's announced "
      "$381M co-financing is pre-existing workforce spending"),
     [2026, 2027, 2028]),
    ("Burundi", "Laboratory commodities",
     "Burundi Government: Lab Commodities ($)",
     ("NEW Burundi Government: lab commodities (Sec 2.2.3)",
      [0, 0, 0, 1360000, 2000000],
      "Sec 2.2.3 New column"),
     ("EXISTING Burundi Government: lab commodities (Sec 2.2.3)",
      [0, 0, 0, 0, 1360000],
      "Sec 2.2.3 Existing column. Burundi has NO pre-MoU funding base (2026 existing = "
      "$0 - the USG funds 100% at baseline); the existing column only rolls forward "
      "prior-year MoU commitments, stored under the existing basis per the uniform "
      "whole-existing-row convention"),
     YEARS),
    ("Burundi", "Other commodities",
     "Burundi Government: Other Commodities ($)",
     ("NEW Burundi Government: commodities (Sec 2.3.3)",
      [0, 637769, 1479895, 1800000, 10259983],
      "Sec 2.3.3 New column (yearly increments); New+Existing reproduce the App.1 totals "
      "exactly"),
     ("EXISTING Burundi Government: commodities (Sec 2.3.3)",
      [0, 0, 637769, 2117664, 3917664],
      "Sec 2.3.3 Existing column. No pre-MoU base (2026 existing = $0); rolls forward "
      "prior-year MoU commitments only"),
     YEARS),
]

# The MoUs' printed government Total columns (gov only), used as the invariant
# that New + Existing reproduce each year's printed total.
PRINTED_TOTALS = {}
for (cty, area), tots in {
    ("Lesotho", "Laboratory commodities"): [1017000, 1317000, 1467000, 1917000, 2597000],
    ("Lesotho", "Other commodities"): [16602000, 18262000, 20088000, 22097000, 24306000],
    ("Sierra Leone", "Laboratory commodities"): [20000, 70000, 145000, 220000, 295000],
    ("Sierra Leone", "Other commodities"):
        [1757325, 3257325, 4757325, 6257325, 7884335],
    ("Madagascar", "Laboratory commodities"):
        [559284, 615212, 676733, 744409, 818848],
    ("Madagascar", "Other commodities"):
        [10483669, 12369843, 14669888, 17712260, 21571191],
    ("Botswana", "Laboratory commodities"): [22403902, 22449642, 22561436],
    ("Botswana", "Frontline lab workers"): [729675, 751565, 774112],
    ("Botswana", "Other commodities"): [20467986, 20467986, 20467986],
    ("Botswana", "Frontline healthcare workers"): [77053167, 83474265, 89895362],
    ("Burundi", "Laboratory commodities"): [0, 0, 0, 1360000, 3360000],
    ("Burundi", "Other commodities"): [0, 637769, 2117664, 3917664, 14177647],
}.items():
    for y, v in zip([2026, 2027, 2028, 2029, 2030], tots):
        PRINTED_TOTALS[(cty, area, y)] = v

already = set(zip(t["Country"], t["Category (as printed in MoU)"].astype(str)))
new_rows, dropped = [], 0
for country, area, drop_cat, new_spec, ex_spec, years in OPS:
    specs = [s for s in (new_spec, ex_spec) if s]
    if any((country, s[0]) in already for s in specs):
        print(f"skip (already split): {country} / {area}")
        continue
    if drop_cat is not None:
        m = ((t["Country"] == country) & (t["Investment area"] == area)
             & (t["Category (as printed in MoU)"] == drop_cat))
        assert m.sum() == len(years), (country, area, drop_cat, int(m.sum()))
        t = t[~m]
        dropped += int(m.sum())
    # invariant: New + Existing reproduce the MoU's printed per-year totals
    # (documented $1-$1k misprints aside) — checked where a Total column exists
    if new_spec and ex_spec:
        for y, n, e in zip(years, new_spec[1], ex_spec[1]):
            tot = PRINTED_TOTALS.get((country, area, y))
            if tot is not None and abs((n + e) - tot) > 1500:
                raise AssertionError((country, area, y, n + e, tot))
    template = t[(t["Country"] == country) & (t["Funder"] == "Government")
                 & (t["Unit"] == "USD")].iloc[0].to_dict()
    for cat, vals, note in specs:
        rowtype = EXISTING_RT if cat.startswith("EXISTING") else "Line item"
        for y, v in zip(years, vals):
            r = dict(template)
            r.update({"Investment area": area, "Year": y, "Amount": float(v),
                      "Row type": rowtype, "Category (as printed in MoU)": cat,
                      "Source note": note, "MoU footnote (verbatim)": "",
                      "MoU footnote location": ""})
            new_rows.append(r)

if new_rows:
    t = pd.concat([t, pd.DataFrame(new_rows)], ignore_index=True)
    t.to_csv(DATA / "budget_tidy.csv", index=False)
    print(f"budget_tidy.csv: dropped {dropped} merged rows, added {len(new_rows)} "
          f"split rows across {len({r['Country'] for r in new_rows})} countries")
else:
    print("nothing to do")

# --------------------------------------------------------------------------
# Part 2 — the four rolling-existing countries (Lesotho, Sierra Leone,
# Madagascar, Burundi): their Existing columns absorb prior-year MoU
# commitments, so the whole column is NOT pre-MoU money. Per the maintainer's
# decision (Sep 2026), only the 2026 existing level — the genuine pre-MoU base,
# held flat — stays in the existing basis; the roll-forward above it returns to
# the main printed band as explicit "CONTINUATION" line items. Burundi's base
# is $0 (the USG funds 100% at baseline), so it keeps no existing rows at all.
# Invariant: flat base + continuation reproduce the printed Existing column.
# Uganda's existing columns roll the same way and follow the same rule
# (extended by maintainer decision, Sep 2026).
REBASE = [
    ("Uganda", "Laboratory commodities",
     "EXISTING GoU: laboratory commodities (Sec 2.2.3)",
     14054109, "CONTINUATION GoU: laboratory commodities "
               "(Sec 2.2.3 Existing above the 2026 base)"),
    ("Uganda", "Other commodities",
     "EXISTING GoU: other commodities (Sec 2.3.3)",
     16754110, "CONTINUATION GoU: other commodities "
               "(Sec 2.3.3 Existing above the 2026 base)"),
    ("Lesotho", "Laboratory commodities", "EXISTING GoL: lab commodities (Sec 2.2.3)",
     1017000, "CONTINUATION GoL: lab commodities (Sec 2.2.3 Existing above the 2026 base)"),
    ("Lesotho", "Other commodities", "EXISTING GoL: commodities (Sec 2.3.3)",
     16602000, "CONTINUATION GoL: commodities (Sec 2.3.3 Existing above the 2026 base)"),
    ("Sierra Leone", "Laboratory commodities", "EXISTING GoSL: lab commodities (Sec 2.2.3)",
     10000, "CONTINUATION GoSL: lab commodities (Sec 2.2.3 Existing above the 2026 base)"),
    ("Sierra Leone", "Other commodities", "EXISTING GoSL: commodities (Sec 2.3.3)",
     378662, "CONTINUATION GoSL: commodities (Sec 2.3.3 Existing above the 2026 base)"),
    ("Madagascar", "Laboratory commodities",
     "EXISTING Government of Madagascar: lab commodities (Sec 2.2.3)",
     559284, "CONTINUATION Government of Madagascar: lab commodities "
             "(Sec 2.2.3 Existing above the 2026 base)"),
    ("Madagascar", "Other commodities",
     "EXISTING Government of Madagascar: commodities (Sec 2.3.3)",
     9803311, "CONTINUATION Government of Madagascar: commodities "
              "(Sec 2.3.3 Existing above the 2026 base)"),
    ("Burundi", "Laboratory commodities",
     "EXISTING Burundi Government: lab commodities (Sec 2.2.3)",
     0, "CONTINUATION Burundi Government: lab commodities "
        "(Sec 2.2.3 Existing column - no pre-MoU base)"),
    ("Burundi", "Other commodities",
     "EXISTING Burundi Government: commodities (Sec 2.3.3)",
     0, "CONTINUATION Burundi Government: commodities "
        "(Sec 2.3.3 Existing column - no pre-MoU base)"),
]

t = pd.read_csv(DATA / "budget_tidy.csv")
already = set(zip(t["Country"], t["Category (as printed in MoU)"].astype(str)))
changed = 0
for country, area, ex_cat, base, cont_cat in REBASE:
    if (country, cont_cat) in already:
        print(f"skip (already rebased): {country} / {area}")
        continue
    m = ((t["Country"] == country) & (t["Investment area"] == area)
         & (t["Category (as printed in MoU)"] == ex_cat))
    assert m.sum() == 5, (country, area, int(m.sum()))
    ex = t[m].sort_values("Year")
    printed_existing = ex["Amount"].tolist()
    assert printed_existing[0] == base or base == 0, (country, area, printed_existing)
    cont_note = ("MoU-era continuation: the printed Existing column minus the flat 2026 "
                 "pre-MoU base of $" + f"{base:,.0f}" + "/yr - prior-year new commitments "
                 "the MoU rolls into its Existing column; kept in the MAIN printed band "
                 "(maintainer decision, Sep 2026)")
    cont_rows = ex.copy()
    cont_rows["Amount"] = [v - base for v in printed_existing]
    cont_rows["Row type"] = "Line item"
    cont_rows["Category (as printed in MoU)"] = cont_cat
    cont_rows["Source note"] = cont_note
    t.loc[m, "Amount"] = float(base)
    t.loc[m, "Source note"] = (
        "Pre-MoU base: the 2026 value of the Sec Existing column, held flat - the level "
        "funded before the MoU; the column's growth (absorbed prior-year new commitments) "
        "is carried separately as a CONTINUATION line item in the main band")
    if base == 0:
        t = t[~m]  # nothing pre-MoU to show
    t = pd.concat([t, cont_rows], ignore_index=True)
    changed += 1
if changed:
    t.to_csv(DATA / "budget_tidy.csv", index=False)
    print(f"rebased {changed} country-areas onto flat pre-MoU bases")

# --------------------------------------------------------------------------
# Part 3 — Mozambique's existing lab workforce (audit follow-up, Sep 2026).
# Sec 2.2.3's lab FTE table prints a GoM Existing column (3,317 pre-MoU stock,
# rolling to 3,377 as new cohorts absorb) that the original harvest missed —
# the baseline sweep used the App.3 HCW cadres only. Record the printed column
# as existing FTE rows; the matching $ value lives in the imputed-baseline
# layer (impute_new_countries.py), like CIV's 1,900 / Uganda's 2,199 lab.
t = pd.read_csv(DATA / "budget_tidy.csv")
MOZ_CAT = "Frontline Lab Workers (Existing # FTEs Funded, Sec 2.2.3)"
if not ((t["Country"] == "Mozambique")
        & (t["Category (as printed in MoU)"] == MOZ_CAT)).any():
    tmpl = t[(t["Country"] == "Mozambique") & (t["Funder"] == "Government")
             & (t["Unit"] == "FTEs")].iloc[0].to_dict()
    rows = []
    for y, v in zip(YEARS, [3317, 3317, 3327, 3347, 3377]):
        r = dict(tmpl)
        r.update({"Investment area": "Frontline lab workers", "Year": y,
                  "Amount": float(v), "Row type": EXISTING_RT,
                  "Category (as printed in MoU)": MOZ_CAT,
                  "Source note": "Sec 2.2.3 Existing column: 3,317 pre-MoU lab "
                                 "FTEs, rolling forward absorbed new cohorts "
                                 "(3,317 + prior-year new). Valued in the "
                                 "imputed-baseline layer at the 2026 stock",
                  "MoU footnote (verbatim)": "", "MoU footnote location": ""})
        rows.append(r)
    t = pd.concat([t, pd.DataFrame(rows)], ignore_index=True)
    t.to_csv(DATA / "budget_tidy.csv", index=False)
    print("added Mozambique existing lab FTE rows (Sec 2.2.3)")
else:
    print("skip (already added): Mozambique existing lab FTEs")

# --------------------------------------------------------------------------
# Part 4 — one FTE convention for all 16 countries (maintainer decision, Sep
# 2026): government EXISTING FTE rows carry the flat pre-MoU base (the 2026
# stock; a base of 0 means no existing rows at all) and government NEW FTE
# rows carry the CUMULATIVE cohort (new + previously absorbed), so flat base +
# cumulative new = the printed Total column in every year. Where a MoU prints
# per-year increments or a rolling Existing column instead, the printed values
# are quoted in the Source note (Uganda's per-cadre columns are also preserved
# verbatim in analysis/uganda_cadre_fte.csv). Idempotent: values are SET.
t = pd.read_csv(DATA / "budget_tidy.csv")
NOTE_FLAT = ("Pre-MoU base held flat per the uniform FTE convention; the printed "
             "Existing column rolls forward absorbed cohorts: {printed}")
NOTE_CUM = ("Cumulative new cohort (new + previously absorbed) per the uniform FTE "
            "convention; printed per-year New column: {printed}")

def set_fte(country, area, cat, values, note):
    m = ((t["Country"] == country) & (t["Investment area"] == area)
         & (t["Category (as printed in MoU)"] == cat) & (t["Unit"] == "FTEs"))
    assert m.sum() == len(values), (country, area, cat, int(m.sum()), len(values))
    idx = t.loc[m].sort_values("Year").index
    old = [int(v) for v in t.loc[idx, "Amount"]]
    t.loc[idx, "Amount"] = [float(v) for v in values]
    t.loc[idx, "Source note"] = note.format(printed=old)
    return old != list(values)

FHW, LAB = "Frontline healthcare workers", "Frontline lab workers"
changed = 0
# rolling Existing columns -> flat pre-MoU base
for c, a, cat, base in [
    ("Mozambique", LAB, "Frontline Lab Workers (Existing # FTEs Funded, Sec 2.2.3)", 3317),
    ("Mozambique", FHW, "Existing # FTEs Funded", 38462),
    ("Uganda", FHW, "Existing # FTEs Funded", 49014),
    ("Uganda", LAB, "Existing # FTEs Funded", 2199),
    ("Côte d'Ivoire", FHW, "Existing # FTEs Funded", 39800),
    ("Côte d'Ivoire", LAB, "Existing # FTEs Funded", 1900),
]:
    changed += set_fte(c, a, cat, [base] * 5, NOTE_FLAT)
# per-year New columns -> cumulative cohorts
for c, a, cat, vals in [
    ("Côte d'Ivoire", FHW, "Frontline healthcare workers - NEW Côte d'Ivoire FTEs",
     [0, 5200, 10400, 15600, 20800]),
    ("Côte d'Ivoire", LAB, "Frontline laboratory workers - NEW Côte d'Ivoire FTEs",
     [0, 250, 500, 750, 1000]),
    ("Cameroon", FHW, "GoC new Frontline Healthcare Worker FTEs (Sec 2.4.3)",
     [0, 0, 1001, 1924, 2846]),
    ("Cameroon", LAB, "GoC new Frontline Lab Worker FTEs (Sec 2.2.3)",
     [0, 0, 62, 125, 187]),
    ("Malawi", FHW, "Government of Malawi: Frontline Healthcare Workers (# FTEs)",
     [0, 351, 739, 1127, 1515]),
    ("Malawi", LAB, "Government of Malawi: Frontline Lab Workers (# FTEs)",
     [0, 99, 198, 380, 479]),
    ("Madagascar", FHW,
     "Government of Madagascar: Frontline Healthcare Workers (# FTEs)",
     [0, 2262, 4660, 7272, 9947]),
    ("Uganda", FHW, "GoU NEW FTEs: epidemiologists", [0, 11, 21, 50, 80]),
    ("Uganda", FHW, "GoU NEW FTEs: medical cadres", [0, 65, 297, 595, 890]),
    ("Uganda", FHW, "GoU NEW FTEs: nurses and midwives", [0, 124, 457, 838, 1435]),
    ("Uganda", FHW, "GoU NEW FTEs: pharmacists", [0, 20, 46, 66, 148]),
    ("Uganda", FHW, "GoU NEW FTEs: social workers", [0, 20, 120, 492, 1092]),
    ("Uganda", LAB, "GoU NEW FTEs: laboratory cadres", [0, 115, 311, 660, 1272]),
    ("Uganda", FHW, "NEW GoU: Human Resources for Health (# FTEs)",
     [0, 5355, 11252, 16701, 19379]),
]:
    changed += set_fte(c, a, cat, vals, NOTE_CUM)
changed += set_fte("Uganda", FHW, "GoU NEW FTEs: CHEWs", [5000, 10000, 14000, 14462],
                   NOTE_CUM)  # printed 2027-2030 only; 2026 CHEW new is blank
# Cameroon's Existing column starts (and stays, pre-MoU) at 0: drop its rows
drop = ((t["Country"] == "Cameroon") & (t["Unit"] == "FTEs")
        & (t["Category (as printed in MoU)"] == "Existing # FTEs Funded"))
if drop.any():
    t = t[~drop]
    changed += 1
    print("dropped Cameroon zero-base existing FTE rows")
# countries whose pre-MoU FTE stock had no tidy rows at all: add them flat
ADD_STOCK = [
    ("Burundi", FHW, 11260, "Sec 2.4.3: 1,169 doctors + 10,091 nurses"),
    ("Burundi", LAB, 1344, "Sec 2.2.3: lab technicians"),
    ("Malawi", FHW, 19127, "Sec 2.4.3 Existing column"),
    ("Malawi", LAB, 639, "Sec 2.2.3 Existing column"),
    ("Sierra Leone", FHW, 12554, "Sec 2.4.3 Existing column"),
    ("Sierra Leone", LAB, 76, "Sec 2.2.3 Existing column (the all-government "
                              "epidemiologists, per App.3)"),
    ("Madagascar", FHW, 5769, "Sec 2.4.3 Existing column"),
    ("Madagascar", LAB, 310, "Sec 2.2.3 Existing column"),
    ("Eswatini", FHW, 754, "Sec 2.4.3 Existing GOKE column"),
    ("Eswatini", LAB, 54, "Sec 2.2.3 Existing GOKE column"),
]
new_rows = []
for c, a, stock, src in ADD_STOCK:
    cat = f"Existing # FTEs Funded ({src.split(':')[0].split(' (')[0]})"
    if ((t["Country"] == c) & (t["Investment area"] == a)
            & (t["Row type"] == EXISTING_RT) & (t["Unit"] == "FTEs")).any():
        continue
    tmpl = t[(t["Country"] == c) & (t["Funder"] == "Government")].iloc[0].to_dict()
    for y in YEARS:
        r = dict(tmpl)
        r.update({"Investment area": a, "Year": y, "Amount": float(stock),
                  "Unit": "FTEs", "Row type": EXISTING_RT,
                  "Category (as printed in MoU)": cat,
                  "Source note": f"Pre-MoU stock held flat ({src}); the printed "
                                 "column rolls absorbed cohorts forward. Valued in "
                                 "the imputed-baseline layer",
                  "MoU footnote (verbatim)": "", "MoU footnote location": ""})
        new_rows.append(r)
if new_rows:
    t = pd.concat([t, pd.DataFrame(new_rows)], ignore_index=True)
t.to_csv(DATA / "budget_tidy.csv", index=False)
print(f"FTE convention: {changed} row-groups normalised, "
      f"{len(new_rows)} existing-stock rows added")

# --------------------------------------------------------------------------
# Part 5 — Mozambique: apportion the printed worker total across its two
# cadres (maintainer decision, Sep 2026). App.1 p.34's footnote prices the
# WHOLE new cohort — "4,893 front-line Healthcare workers ... $46,973,106",
# where 4,893 = 4,788 HCW + 105 lab exactly — and the derived per-year
# residual had been parked wholly on the HCW line. That made the lab panel
# taper with the USG exit even though total lab FTEs are constant (3,422
# every year: the GoM absorbs exactly what the USG hands over). The lab share
# is now carved out at the own USG marginal lab rate ($6,600/FTE, the rate the
# baseline layer uses on the same panel): cumulative lab FTEs 10/30/60/105 ->
# $66k/$198k/$396k/$693k, with the HCW line reduced by the same amounts.
# Totals unchanged; a pro-rata FTE split of the blended residual (~$3,947/FTE)
# would give ~$1.0M instead of $1.35M - noted, not used.
t = pd.read_csv(DATA / "budget_tidy.csv")
MOZ_LAB_CAT = "Frontline Lab Workers ($, share of the 4,893-worker total)"
if not ((t["Country"] == "Mozambique")
        & (t["Category (as printed in MoU)"] == MOZ_LAB_CAT)).any():
    LAB_SHARE = {2026: 0.0, 2027: 66000.0, 2028: 198000.0,
                 2029: 396000.0, 2030: 693000.0}
    fhw = ((t["Country"] == "Mozambique") & (t["Funder"] == "Government")
           & (t["Category (as printed in MoU)"]
              == "Frontline Healthcare Workers ($, derived residual)"))
    assert fhw.sum() == 5
    for i in t.loc[fhw].index:
        t.loc[i, "Amount"] -= LAB_SHARE[int(t.loc[i, "Year"])]
    t.loc[fhw, "Source note"] = (
        "Derived residual of the printed GoM totals, NET of the lab-cadre share "
        "(cumulative lab FTEs x $6,600 - see the Frontline Lab Workers rows). "
        "App.1 p.34's $46,973,106 footnote prices all 4,893 new workers "
        "(4,788 HCW + 105 lab) together")
    tmpl = t.loc[fhw].iloc[0].to_dict()
    rows = []
    for y, v in LAB_SHARE.items():
        r = dict(tmpl)
        r.update({"Investment area": "Frontline lab workers", "Year": y,
                  "Amount": v, "Category (as printed in MoU)": MOZ_LAB_CAT,
                  "Source note": "Lab-cadre share of the printed $46,973,106 "
                                 "worker total (4,893 = 4,788 HCW + 105 lab): "
                                 "cumulative lab FTEs 10/30/60/105 x $6,600 "
                                 "(own USG marginal rate, as in the baseline "
                                 "layer). Carved OUT of the HCW residual - "
                                 "totals unchanged. A pro-rata FTE split at "
                                 "the blended ~$3,947/FTE would give ~$1.0M "
                                 "over the term instead of $1.35M"})
        rows.append(r)
    t = pd.concat([t, pd.DataFrame(rows)], ignore_index=True)
    t.to_csv(DATA / "budget_tidy.csv", index=False)
    print("Mozambique: lab share carved out of the HCW worker total")
else:
    print("skip (already apportioned): Mozambique lab share")
