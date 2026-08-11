# Government HRH contributions across all nine MoUs — printed, imputed, and harvested

*Derived analysis, 11 Aug 2026 (rev. 2 — new-vs-existing FTE correction, same day). Extends the Cameroon pilot (`Cameroon_FTE_rate_analysis.md`) to every country. Reproducible via `analysis/fte_rate_imputation_all.py`; imputed rows in `imputed_gov_hrh_all_countries.csv`; per-country summary in `gov_hrh_summary_by_country.csv`; harvested Mozambique cadre tables in `moz_cadre_fte.csv`.*

## Rev. 2: reading the New / Existing columns correctly

The MoU FTE tables print a "New # FTEs Funded" and an "Existing # FTEs Funded" column, and *Existing is written from each year's own perspective*: Existing(t) = pre-MoU baseline + cumulative prior-year new absorptions (Cameroon labs 2029 shows 62 "existing" — the 2028 cohort). Since a worker absorbed in year t draws salary in every later year, the government's funding base each year is **new + previously absorbed**, not the new column alone. This revision corrects Cameroon (labs 62→125→187 funded FTEs, not 62/63/62; HCW 1,001→1,924→2,846), Côte d'Ivoire and Uganda labs. Ethiopia, Mozambique and Rwanda were already captured as per-year totals (their series mirror the USG drawdown or match the printed Total column) and are unchanged. Pre-MoU baseline workforces (Côte d'Ivoire: 39,800 HCW + 1,900 lab; Uganda: 2,199 lab, printed inside the Existing columns) are **excluded from imputation** — baseline effort, not MoU co-financing.

## The MoUs themselves validate the method — three times

Before imputing anything, three MoUs turn out to do this arithmetic internally, which pins down both the method and the "flat nominal rate" choice:

**Ethiopia (HCW)** is the cleanest case in the whole dataset. The government's printed $ equals the USG FTE drawdown times the USG 2026 unit rate ($1,748.29) to the dollar, every year: 2027 printed $3,543,790 = 2,027 handed-over FTEs × $1,748.29; 2029 printed $10,629,621 = 6,080 × rate; 2030 printed $14,173,411 = full 8,107 × rate. The government side is literally a mirror of the USG drawdown priced at the USG rate.

**Kenya (lab)** prints a government rate of $12,548/FTE in 2028–30 — identical to its USG 2026 rate.

**Mozambique (lab)** prices with a fixed + marginal structure: USG lab $ = $165,200 + $6,600 × FTEs, fitting all four funded years with zero residual. Its government HCW $ runs at ~$4,000 marginal per FTE, flat.

So where a country gives us FTEs without $, applying that country's own USG unit rate (flat, no inflation adjustment) is not an invention — it is the MoUs' own convention.

## What was imputed, and with what

| Country | Line | Gov FTE-yrs funded | Rate | Gov $ (central) | Range | Confidence |
|---|---|---|---|---|---|---|
| Ethiopia | Lab workers | 197 | $5,488 (own USG, constant all years) | **$1.08M** | 1.08–1.11M | high |
| Mozambique | Lab workers | 205 | $6,600 (own USG marginal, exact fit) | **$1.35M** | 1.35–1.68M | high |
| Cameroon | HCW + lab | 5,771 + 374 | own USG 2026 rates | **$27.70M** | 25.4–30.9M | medium |
| Rwanda | HCW | 7,061 | $1,563 (own USG 2026) | **$11.03M** | 11.0–18.0M | low |
| Rwanda | Lab workers | 1,120 | $2,700 (own USG 2026) | **$3.02M** | 3.0–6.8M | low |
| Uganda | Lab workers | 2,358 | $3,396 (peer median × wage factor) | **$8.01M** | 4.4–14.6M | low |
| Côte d'Ivoire | HCW | 52,000 | $3,368 (peer gov median) | **$175.13M** | 90.9–236.1M | low |
| Côte d'Ivoire | Lab workers | 2,500 | $6,186 (peer lab median) | **$15.46M** | 6.2–31.4M | low |

Confidence notes. Ethiopia and Mozambique labs are handover mirrors (gov FTEs ramp up exactly as USG FTEs ramp down) priced at rates the MoU applies consistently — these are as close to "printed" as an imputation gets. Rwanda's $ (App.1) and FTE (Sec 2.2.3/2.4.3) series visibly misalign (its lab rate would swing from $2,700 to $104,042), so only the 2026 rate is usable and the blended-rate upper bound is wide. Uganda's lab rate is scaled down from the peer lab median by Uganda's own wage level (its gov HCW rate, $1,849, is 55% of the peer median). Côte d'Ivoire prints no HRH $ anywhere — USG side included — so both lines rest entirely on peer rates; at ~$191M it is by far the largest and least certain imputation (5,200 new HCW absorbed *per year*, cumulating to 20,800 funded in 2030), its USG HCW FTE series mixes salaried staff with ITN/SMC campaign workers, and its printed 2028 Total column is internally inconsistent (52,500 vs the 50,200 its own columns imply — the difference is that year's USG count). Check the cadre and the table arithmetic before using the CIV figure externally.

Peer rate benchmarks used: government HCW $/FTE — Ethiopia $1,748, Uganda $1,849, Kenya $3,368, Mozambique $3,989, Liberia $4,541 (median $3,368). Lab $/FTE — Liberia $2,500, Ethiopia $5,488, Cameroon $6,186, Mozambique $6,600, Kenya $12,548 (median $6,186).

## The full picture: government HRH effort across the nine MoUs

| Component | 5-yr value |
|---|---|
| Printed in the MoUs (Ethiopia, Kenya†, Liberia, Moz HCW, Nigeria, Uganda HCW) | **$696.1M** |
| Imputed, own-country rates (Cameroon, Ethiopia lab, Moz lab) | **$30.1M** |
| Imputed, low confidence (Rwanda, Uganda lab, Côte d'Ivoire) | **$212.7M** |
| **Total government frontline-HRH effort** | **≈ $939M** |

† Kenya's series runs six years (2026–2031). Nigeria's $297.6M is printed without any FTE counts, so its implied rate can't be checked.

Imputation closes the last ~26% of the picture: roughly $939M of government HRH commitments across the nine countries, of which $696M was printed and ~$243M recovered from FTE tables. About $191M of the imputed total sits in Côte d'Ivoire alone on peer rates only — flag it wherever this is presented.

## Bonus harvest: Mozambique's cadre tables (App. 3, pp. 36–37)

Mozambique's appendix breaks the HCW commitment into six cadre tables — G2G absorption (400/yr), Clinical Officers, Doctors, Nurses, Pharmacy Technicians, CHWs/APS — each with USG-funded, government-new, government-existing and government-total FTEs per year. Now captured in `moz_cadre_fte.csv`. Three things it shows:

1. **It reconciles exactly with the tidy data.** New-hire columns sum to 1,180 / 1,188 / 1,208 / 1,212 per year — precisely the increments in the gov FTE series — and the USG cadre columns sum to 8,166 fewer than the headline USG FTE line in every year, confirming that known source-document gap.
2. **The government's existing workforce dwarfs everything in this analysis.** Existing government FTEs start at 38,462 in 2026 (10,113 clinical officers, 12,336 nurses, 8,959 CHWs, 4,585 pharmacy techs, 2,469 doctors) and reach 43,250 by 2030 — about 204,000 FTE-years over the term. Priced illustratively at Mozambique's own ~$4,000 marginal rate that is ~$800M of baseline workforce spending in one country, against $47M of printed "new" commitment. This is the concrete counterpart of the Cameroon finding that co-investment aggregates embed unitemised baseline effort.
3. **Cadre mix explains blended rates.** The USG-funded pool is ~85% CHWs (9,899 of 11,632 attributable FTEs in 2026), which is why blended $/FTE rates sit far below professional salaries.

Only Mozambique prints cadre tables at this depth; none of the other eight MoUs have an equivalent to harvest (Kenya's FELTP salary table in §2.1.2.5 is the closest, already captured under its HCW rows).

## Caveats

All rates are nominal USD as printed; imputations inherit whatever non-salary costs sit inside USG lines. FTEs are read as FTE-years funded in the year. Rwanda's 2030 lab figure (289 vs 277) follows App.1 over the narrative. Government FTE series for Ethiopia/Mozambique labs are takeover mirrors of USG drawdowns, so "government contribution" there means absorbing USG-funded positions, not net new hiring. Côte d'Ivoire's imputation is a peer-rate estimate only and should not be quoted without its range.
