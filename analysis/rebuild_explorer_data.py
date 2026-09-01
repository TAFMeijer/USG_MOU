"""Regenerate the `const DATA = {...}` blob embedded in explorer.html from
data/budget_series.csv, and mirror the result to docs/index.html (the GitHub Pages copy).

Basis: printed rows only (`Printed in MoU` + `Printed in MoU (existing/pre-MoU)`), matching
the standalone explorer's stated definition of government = new co-financing plus existing
government funding. Imputed series are deliberately excluded - the explorer has no toggle
for them.

Years a country's MOU does not cover are emitted as `null`, not 0, so a shorter agreement
(Botswana, 2026-2028) shows a line that ends rather than a line that falls to zero.

  python analysis/rebuild_explorer_data.py
"""
from pathlib import Path
import json
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
YEARS = [2026, 2027, 2028, 2029, 2030]
PRINTED = ["Printed in MoU", "Printed in MoU (existing/pre-MoU)"]

s = pd.read_csv(ROOT / "data" / "budget_series.csv")
s = s[s["Basis"].isin(PRINTED)]

# which years does each country's MOU actually cover?
covered = s.groupby("Country")["Year"].apply(set).to_dict()

agg = s.groupby(["Country", "Investment area", "Funder", "Year"], as_index=False)["Amount"].sum()
lookup = {(r.Country, r._2, r.Funder, r.Year): r.Amount for r in agg.itertuples()}

series = []
for (cty, area, funder), _ in agg.groupby(["Country", "Investment area", "Funder"]):
    vals = [lookup.get((cty, area, funder, y)) if y in covered[cty] else None for y in YEARS]
    vals = [0.0 if (v is None and y in covered[cty]) else v for v, y in zip(vals, YEARS)]
    nums = [v for v in vals if v is not None]
    if not nums or max(nums) <= 0:
        continue
    series.append({"area": area, "country": cty, "funder": funder,
                   "values": vals, "max": max(nums)})

series.sort(key=lambda r: (r["country"], r["area"], r["funder"]))
blob = json.dumps({"years": YEARS, "series": series}, separators=(", ", ": "))

src = (ROOT / "explorer.html").read_text(encoding="utf-8")
i = src.index("const DATA = ")
j = src.index("\n", i)
out = src[:i] + "const DATA = " + blob + ";" + src[j:]
(ROOT / "explorer.html").write_text(out, encoding="utf-8")
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "index.html").write_text(out, encoding="utf-8")

short = {c: sorted(y) for c, y in covered.items() if len(y) < len(YEARS)}
print(f"explorer.html + docs/index.html: {len(series)} series, "
      f"{len({r['country'] for r in series})} countries, "
      f"{len({r['area'] for r in series})} investment areas")
print("short-term MOUs (null-padded):", short or "none")
