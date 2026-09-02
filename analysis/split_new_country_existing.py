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
