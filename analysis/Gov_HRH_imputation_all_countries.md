# Government HRH contributions across the MoUs — printed, imputed, and harvested

*Derived analysis, 11 Aug 2026; rev. 4, 2 Sep 2026 (Côte d'Ivoire re-based on its own printed rates; Liberia 2027 lab cell corrected). Extends the Cameroon pilot (`Cameroon_FTE_rate_analysis.md`) to every country. Reproducible via `analysis/fte_rate_imputation_all.py`; imputed rows in `imputed_gov_hrh_all_countries.csv`; per-country summary in `gov_hrh_summary_by_country.csv`; cadre tables in `moz_cadre_fte.csv` and `uganda_cadre_fte.csv`.*

## Rev. 4: Côte d'Ivoire, re-based on its own printed rates

Appendix 1 of the full Côte d'Ivoire text (pp. 25–26) prices the **USG's** frontline
workers, which the 24-page scan the original transcription used never showed: healthcare
workers $13.4M against 5,556 **core** FTEs = **$2,411.81** (2027–28 give $2,666.67 /
$2,521.74; the seasonal CHW column is excluded, and 2029–30 print dollars against 0 core
FTEs so they yield no rate at all), and lab workers $1.0M against 65 FTEs = **$15,384.62**
(2027–28: $15,555.56 / $16,000.00). The premise "CIV prints no HRH $ anywhere" is therefore
false — but only on the USG side. Its **government** column still prices commodities alone,
so the imputation stands and only its rate basis changes:

| Line | Was (peer rates) | Now (own rates) |
|---|---|---|
| HCW, 52,000 FTE-years | $3,601/FTE → $187.26M | $2,411.81/FTE → **$125.41M** |
| Lab, 2,500 FTE-years | $6,186/FTE → $15.46M | $15,384.62/FTE → **$38.46M** |
| CIV total imputed | $202.7M | **$163.88M** (range $141–227M) |
| CIV pre-MoU baseline (39,800 HCW + 1,900 lab) | $775.4M | **$626.10M** |

The lab figure lands well outside its old $6.2–31.4M peer-rate range: an Ivorian lab worker
costs the USG roughly 2.5× the peer-government median. Confidence rises from *low* to
*medium* — an in-country price now exists — but the standing caveat that a USG line carries
non-salary cost a government would not bear still applies, which is why the range brackets
the own rate against the peer median rather than against the own years alone.

This revision also carries the Liberia correction: the released text prints $152,400 for
the 2027 government frontline-lab cell where the superseded scan printed $1,341,984,
lowering printed government HRH by $1.19M.

## Rev. 3: Uganda, corrected from its cadre tables

The Uganda gov HCW series previously used (10,584/11,588/10,520/4,714) was a **double count in the aggregation**: the tidy data faithfully stores both App.3's national roll-up (New = 5,355/5,897/5,449/2,678) *and* its cadre breakdown as line items, and summing them added the roll-up to its own parts (5,355 + 5,229 cadre-sum = 10,584). The roll-up is now tagged as a subtotal; the seven cadre tables (`uganda_cadre_fte.csv` — labs, epidemiologists, medical, nurses & midwives, CHEWs, pharmacists, social workers) sum to the national New column **exactly**, per year, and data is stored at cadre level and rolled up from there. Three consequences:

1. **Uganda's real rate.** Printed gov $ ÷ national new cohort = $3,581 / $3,591 / $3,611 — near-flat — then $6,337 in 2030 as the cohort mix shifts from CHEWs (85–93% of early cohorts) to clinical cadres. Own rate: **$3,601** (median), not the $1,849 the wrong denominator produced.
2. **Uganda's printed $ prices only each year's NEW cohort.** Absorbed cohorts move into the Existing column unpriced. Their continued salaries — 32,222 HCW + 1,086 lab FTE-years — are now imputed at the own rate: **+$122.8M** on top of the printed $77.0M. No other MoU works this way (Ethiopia, Mozambique, Liberia, Kenya all price cumulative funding).
3. **Ripple effects.** The peer gov HCW median moves from $3,368 to **$3,601** (lifting Côte d'Ivoire to $187.3M — superseded by rev. 4), and Uganda's baseline — 49,014 HCW (national 51,213 net of its 2,199 lab component, which has its own series) — revalues to **$883M**, making Uganda the largest tabulated baseline of all nine countries.

## Rev. 2: reading the New / Existing columns correctly

The MoU FTE tables print a "New # FTEs Funded" and an "Existing # FTEs Funded" column, and *Existing is written from each year's own perspective*: Existing(t) = pre-MoU baseline + cumulative prior-year new absorptions (Cameroon labs 2029 shows 62 "existing" — the 2028 cohort). Since a worker absorbed in year t draws salary in every later year, the government's funding base each year is **new + previously absorbed**, not the new column alone. This revision corrects Cameroon (labs 62→125→187 funded FTEs, not 62/63/62; HCW 1,001→1,924→2,846), Côte d'Ivoire and Uganda labs. Ethiopia, Mozambique and Rwanda were already captured as per-year totals (their series mirror the USG drawdown or match the printed Total column) and are unchanged. Pre-MoU baseline workforces (Côte d'Ivoire: 39,800 HCW + 1,900 lab; Uganda: 2,199 lab, printed inside the Existing columns) are **excluded from imputation** — baseline effort, not MoU co-financing.

## The MoUs themselves validate the method — three times

Before imputing anything, three MoUs turn out to do this arithmetic internally, which pins down both the method and the "flat nominal rate" choice:

**Ethiopia (HCW)** is the cleanest case in the whole dataset. The government's printed $ equals the USG FTE drawdown times the USG 2026 unit rate ($1,748.29) to the dollar, every year: 2027 printed $3,543,790 = 2,027 handed-over FTEs × $1,748.29; 2029 printed $10,629,621 = 6,080 × rate; 2030 printed $14,173,411 = full 8,107 × rate. The government side is literally a mirror of the USG drawdown priced at the USG rate.

**Kenya (lab)** prints a government rate of $12,548/FTE in 2028–30 — identical to its USG 2026 rate.

**Mozambique (lab)** prices with a fixed + marginal structure: USG lab $ = $165,200 + $6,600 × FTEs, fitting all four funded years with zero residual. Its government HCW $ runs at ~$4,000 marginal per FTE, flat.

So where a country gives us FTEs without $, applying that country's own USG unit rate (flat, no inflation adjustment) is not an invention — it is the MoUs' own convention.

## Is Uganda really unique? The pricing-convention test

The *bookkeeping* is universal: every MoU's FTE tables roll absorbed cohorts forward with the same New/Existing logic (Existing(t) = baseline + prior new). The question is what the **dollars** on top of it price. That is testable wherever government $ is printed: divide the $ series by cumulative-funded FTEs and by new-cohort FTEs — whichever gives a **flat rate** is the convention the MoU uses.

| Country | $ ÷ cumulative funded | $ ÷ new cohort | Verdict |
|---|---|---|---|
| Ethiopia | **$1,748 · 1,748 · 1,748 · 1,748** | 1,748 → 3,497 → 5,247 → 6,992 | cumulative |
| Mozambique | **$3,981 · 3,997 · 4,000 · 3,865** | 3,981 → 7,968 → 11,842 → 15,268 | cumulative |
| Liberia | **$5,337 · 4,129 · 4,363 · 4,541** (2027–30) | 5,629 → 8,003 → 17,571 → 23,620 | cumulative |
| Kenya | **$3,441 · 3,441 · 3,441** (constant 13,293 stock funded annually) | same arithmetic (stock = cohort) | cumulative |
| Uganda | 3,581 → 1,882 → 1,178 → 876 | **$3,581 · 3,591 · 3,611** (· 6,337) | **new-cohort** |

Four of five price the whole absorbed stock every year; **Uganda alone prices the incoming cohort once** and lets it disappear into the unpriced Existing column — plausibly because its gov $ series comes from the Appendix 1 co-funding column ("new funding") rather than a section funding-plan table.

The two unpriced countries can be cross-checked indirectly, and both point cumulative. **Cameroon**: modelling its printed commodities-&-HRH co-investment aggregate with cumulative HRH explains 48% → 77% → **96%** of the printed values in 2028–30, versus a flat ~50% under new-only pricing — the MoU's own aggregate endorses cumulative. **Rwanda**: its commodity tables price the takeover cumulatively *in dollars* (Total = New + cumulative Existing: $612k → $12.64M → $17.60M), so the same drafting logic applied to its HRH FTEs implies cumulative. **Côte d'Ivoire** stays untestable on the cumulative-vs-new question: App.1's government table prints its FTEs cumulatively but attaches no dollars to them, so nothing in the document prices a government worker.

## What was imputed, and with what

| Country | Line | Gov FTE-yrs funded | Rate | Gov $ (central) | Range | Confidence |
|---|---|---|---|---|---|---|
| Ethiopia | Lab workers | 197 | $5,488 (own USG, constant all years) | **$1.08M** | 1.08–1.11M | high |
| Mozambique | Lab workers | 205 | $6,600 (own USG marginal, exact fit) | **$1.35M** | 1.35–1.68M | high |
| Cameroon | HCW + lab | 5,771 + 374 | own USG 2026 rates | **$27.70M** | 25.4–30.9M | medium |
| Rwanda | HCW | 7,061 | $1,563 (own USG 2026) | **$11.03M** | 11.0–18.0M | low |
| Rwanda | Lab workers | 1,120 | $2,700 (own USG 2026) | **$3.02M** | 3.0–6.8M | low |
| Uganda | HCW (continuation) | 32,222 | $3,601 (own new-cohort rate) | **$116.04M** | 115.4–128.0M | medium |
| Uganda | Lab (continuation) | 1,086 | $6,186 (peer lab median) | **$6.72M** | 2.7–6.7M | low |
| Côte d'Ivoire | HCW | 52,000 | $2,412 (own USG 2026, App.1) | **$125.41M** | 125.4–187.3M | medium |
| Côte d'Ivoire | Lab workers | 2,500 | $15,385 (own USG 2026, App.1) | **$38.46M** | 15.5–40.0M | medium |

Confidence notes. Ethiopia and Mozambique labs are handover mirrors (gov FTEs ramp up exactly as USG FTEs ramp down) priced at rates the MoU applies consistently — these are as close to "printed" as an imputation gets. Rwanda's $ (App.1) and FTE (Sec 2.2.3/2.4.3) series visibly misalign (its lab rate would swing from $2,700 to $104,042), so only the 2026 rate is usable and the blended-rate upper bound is wide. Uganda's lab rate is scaled down from the peer lab median by Uganda's own wage level (its gov HCW rate, $1,849, is 55% of the peer median). Côte d'Ivoire prices HRH on the USG side only (App.1), so both government lines are imputed at those rates; at ~$164M it is still the largest imputation (5,200 new HCW absorbed *per year*, cumulating to 20,800 funded in 2030), its USG HCW FTE series mixes salaried staff with ITN/SMC campaign workers, and its printed 2028 Total column is internally inconsistent (52,500 vs the 50,200 its own columns imply — the difference is that year's USG count). Check the cadre and the table arithmetic before using the CIV figure externally.

Peer rate benchmarks used: government HCW $/FTE — Ethiopia $1,748, Uganda $1,849, Kenya $3,368, Mozambique $3,989, Liberia $4,541 (median $3,368). Lab $/FTE — Liberia $2,500, Ethiopia $5,488, Cameroon $6,186, Mozambique $6,600, Kenya $12,548 (median $6,186).

## The full picture: government HRH effort across the sixteen MoUs

| Component | 5-yr value |
|---|---|
| Printed in the MoUs (all 16 texts; Ethiopia, Kenya†, Liberia, Moz HCW, Nigeria, Uganda HCW new cohorts and the seven newest) | **$1,001.9M** |
| Imputed, high/medium confidence (Cameroon, Ethiopia lab, Moz lab, Uganda HCW continuation, Côte d'Ivoire) | **$310.1M** |
| Imputed, low confidence (Rwanda, Uganda lab continuation) | **$20.8M** |
| **Total government frontline-HRH commitment** | **≈ $1.33bn** |

† Kenya's series runs six years (2026–2031). Nigeria's $297.6M is printed without any FTE counts, so its implied rate can't be checked.

Imputation closes ~25% of the picture: roughly $1.33bn of government HRH commitments across the sixteen countries, of which $1,002M is printed and ~$331M recovered from FTE tables. The two big imputed blocks — Côte d'Ivoire's ~$164M and Uganda's ~$123M continuation — deserve flags wherever this is presented, for different reasons: CIV's prices government workers at the rates the USG pays, Uganda's rests on a well-identified own rate but a pricing convention the flat-rate test (above) shows no other MoU uses.

## The pre-MoU baseline workforce: visible and filterable

Four MoUs tabulate the government's *existing* workforce — the pre-MoU stock inside the "Existing # FTEs Funded" columns (its 2026 value, before any absorption rolls in). Valued at the same rates as the imputation (`imputed_baseline_workforce.csv`):

| Country | Baseline FTEs (2026 stock) | Rate basis | 5-yr value |
|---|---|---|---|
| Uganda | 49,014 HCW + 2,199 lab (national 51,213 net of lab) | own new-cohort rate ($3,601) / peer lab | **$950.6M** |
| Côte d'Ivoire | 39,800 HCW + 1,900 lab | own USG 2026 rates (App.1) | **$626.1M** |
| Mozambique | 38,462 HCW (App. 3 cadres) | own gov rate (~$3,989) | **$767.1M** |
| Liberia | 6,577 HCW + 538 lab | own gov rates | **$156.0M** |
| **Total tabulated baseline effort** | | | **≈ $2.65bn** |

Kenya, Cameroon, Ethiopia, Rwanda and Nigeria print no workforce baseline (their Existing columns start at zero or don't exist). Note the two table variants: CIV/Uganda/Mozambique roll absorbed cohorts into Existing over time (baseline = the 2026 value), while Liberia holds Existing constant at the baseline and accumulates absorption inside its New column — both reduce to the same decomposition. This ~$2.65bn is **baseline effort, not MoU co-financing** — two and a half times the ~$1.07bn of MoU HRH commitments — and it is exactly the "existing government funding" that co-funding summaries fold into their government headline columns. In the dashboard it is a separate dotted series with its own toggle, so it can be seen and excluded at will.

## Bonus harvest: Mozambique's cadre tables (App. 3, pp. 36–37)

Mozambique's appendix breaks the HCW commitment into six cadre tables — G2G absorption (400/yr), Clinical Officers, Doctors, Nurses, Pharmacy Technicians, CHWs/APS — each with USG-funded, government-new, government-existing and government-total FTEs per year. Now captured in `moz_cadre_fte.csv`. Three things it shows:

1. **It reconciles exactly with the tidy data.** New-hire columns sum to 1,180 / 1,188 / 1,208 / 1,212 per year — precisely the increments in the gov FTE series — and the USG cadre columns sum to 8,166 fewer than the headline USG FTE line in every year, confirming that known source-document gap.
2. **The government's existing workforce dwarfs everything in this analysis.** Existing government FTEs start at 38,462 in 2026 (10,113 clinical officers, 12,336 nurses, 8,959 CHWs, 4,585 pharmacy techs, 2,469 doctors) and reach 43,250 by 2030 — about 204,000 FTE-years over the term. Priced illustratively at Mozambique's own ~$4,000 marginal rate that is ~$800M of baseline workforce spending in one country, against $47M of printed "new" commitment. This is the concrete counterpart of the Cameroon finding that co-investment aggregates embed unitemised baseline effort.
3. **Cadre mix explains blended rates.** The USG-funded pool is ~85% CHWs (9,899 of 11,632 attributable FTEs in 2026), which is why blended $/FTE rates sit far below professional salaries.

Only Mozambique prints cadre tables at this depth; none of the other eight MoUs have an equivalent to harvest (Kenya's FELTP salary table in §2.1.2.5 is the closest, already captured under its HCW rows).

## Caveats

All rates are nominal USD as printed; imputations inherit whatever non-salary costs sit inside USG lines. FTEs are read as FTE-years funded in the year. Rwanda's 2030 lab figure (289 vs 277) follows App.1 over the narrative. Government FTE series for Ethiopia/Mozambique labs are takeover mirrors of USG drawdowns, so "government contribution" there means absorbing USG-funded positions, not net new hiring. Côte d'Ivoire's imputation prices government workers at USG rates and should not be quoted without its range.
