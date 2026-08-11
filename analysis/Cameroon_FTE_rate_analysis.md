# Back-engineering government $ for labs & healthcare workers — Cameroon pilot

*Derived analysis, 11 Aug 2026. Reproducible via `analysis/fte_rate_imputation.py` on `data/budget_tidy.csv`. Nothing here is printed in the MoU unless flagged as such.*

## The question

Cameroon's MoU gives government FTE commitments for frontline lab workers and healthcare workers, but no government $ for those lines (only USG $). Can we derive a $/FTE rate from the USG side (2026 budget ÷ USG-funded FTEs), check its consistency, apply it to the government FTEs — and does summing the resulting line items get close to the $450M commitment?

## 1. The USG $/FTE rate is only meaningful in 2026

| Year | HCW $/FTE | Lab $/FTE | USG total YoY | HCW $ YoY | Lab $ YoY |
|---|---|---|---|---|---|
| 2026 | $4,400 | $6,186 | — | — | — |
| 2027 | $3,991 | $5,609 | −9.3% | −9.3% | −9.3% |
| 2028 | $4,676 | $6,586 | −6.1% | −6.1% | −6.3% |
| 2029 | $6,126 | $8,910 | −15.1% | −15.1% | −15.2% |
| 2030 | $8,834 | $14,839 | −34.3% | −34.3% | −33.8% |

The rate is **not** consistent across years, and the pattern is not inflation (implied growth swings from −9% to +25%). The explanation is in the YoY columns: **every USG line item tracks the total USG glide path exactly** (−9.3, −6.1, −15.1, −34.3), while FTE targets fall on a different, steeper trajectory (0, −20, −36, −57%). The USG $ lines are pro-rata slices of a shrinking envelope, not unit-cost × FTE. So the only year where $ ÷ FTE is a clean unit cost is 2026, the full-funding year — which is the rate proposed: **HCW $4,400/FTE-yr, lab workers $6,186/FTE-yr**.

## 2. Cross-country validation: the method is sound, and flat-nominal is right

Several other MoUs *do* print government-side $ and FTEs, which lets us test both the rate level and the inflation question (full table in `fte_rates_all_countries.csv`):

| Country | Line | Government $/FTE by year | Pattern |
|---|---|---|---|
| Mozambique | HCW | 3,981 → 3,997 → 4,000 → 3,865 | flat ~$4.0k |
| Kenya | HCW | 3,318 → 3,368 → 3,383 | flat ~$3.3k |
| Kenya | Lab | 12,548 → 12,548 → 12,548 | **identical to Kenya's USG 2026 rate ($12,548)** |
| Liberia | HCW | 4,808 → 4,074 → 4,363 → 4,541 (2027–30) | ~$4.1–4.8k |
| Uganda | HCW | 1,812 → 1,828 → 1,870 (→ 3,600 in 2030) | flat ~$1.8k, then jump |

Three takeaways. First, Kenya's MoU literally applies the USG 2026 lab rate to government FTEs — the exact method proposed here is used inside at least one MoU. Second, government rates are **flat nominal** everywhere; no MoU inflation-adjusts. Third, Cameroon's $4,400 HCW rate sits squarely in the peer band ($1.8k–4.5k), so the imputation is credible in level, not just in method. One caution: Kenya's government HCW rate ($3.3k) is ~2× its USG HCW rate ($1.6k), so governments sometimes cost the same worker higher (civil-service scales) — the imputed figures below are best read as a floor.

## 3. Imputed government contribution (Cameroon)

Government FTEs are zero in 2026–27, then lab 62/63/62 and HCW 1,001/923/922 in 2028–30 (187 and 2,846 FTE-years respectively).

| Scenario | Lab $ | HCW $ | HRH total | + new commodities ($10.4M) |
|---|---|---|---|---|
| **A: flat 2026 USG rate (canonical)** | **$1.16M** | **$12.52M** | **$13.68M** | **$24.11M** |
| B: 2026 rate + 3%/yr inflation | $1.26M | $13.68M | $14.94M | $25.37M |
| C: blended 5-yr USG rate | $1.31M | $13.93M | $15.24M | $25.67M |
| D: peer-gov rate (Moz $4.0k HCW) | $1.16M | $11.38M | $12.54M | $22.98M |

The scenario spread is narrow (±10%), so the answer is robust to the rate choice: the government's itemised labs & HCW commitment is worth **~$13–15M**, and all itemised "new" government line items together are worth **~$24M** over the MoU term (~$30M if the "existing/continuing" commodity rows are included).

## 4. Does this get close to $450M? No — and the MoU says why

Appendix 1 (p.23) nests three different numbers:

| Level | 5-yr value | What it is |
|---|---|---|
| Total health expenditure increase over 2025 baseline | **$450M** | Macro budget commitment ($30M→$150M/yr, cumulative increments); 1:1 USG reduction if missed |
| "Within" it: commodities & HRH co-investment | **$72.6M** | Printed aggregate ($11.67M→$20.29M/yr) |
| Within that: itemised new minimums (incl. imputed HRH) | **~$24M** | The line items — the only part that is specified |

Summing line items gets to ~5% of $450M, and even the printed co-investment aggregate is only 16% of it. This is by construction, not by data gap: the $450M is the outer envelope (total government health spending growth — salaries, infrastructure, everything), sized to headline-match the USG's $399.25M, and the MoU's own language places the co-investment "within" it. **No amount of line-item summing will reach $450M**, because ~$377M of it is deliberately unitemised.

The more interesting gap is the middle one: itemised + imputed lines explain only **~⅓ of the $72.6M** co-investment aggregate. The aggregate runs at $11.67M/yr in 2026–27 when every itemised government line is zero — so it must embed ~$11.7M/yr of existing/baseline commodity & HRH spending that the MoU never itemises. Closing the residual gap with the government FTEs alone would require $11–15k/FTE, ~2.5–3× the USG rate — implausible as salaries, plausible as baseline + civil-service costing.

## 5. Bottom line

The back-engineering works and is validated by peer MoUs (Kenya does exactly this internally; use the flat 2026 rate, no inflation adjustment). It prices Cameroon's government labs & HCW commitment at **~$13.7M** and total itemised government effort at **~$24M**. It does not bring line items close to $450M — instead it shows precisely how the $450M decomposes: **$450M pledge ⊃ $72.6M co-investment ⊃ ~$24M specified line items**, i.e. only ~5% of the headline government commitment is traceable to concrete, priceable deliverables. That framing — "what share of the headline pledge is itemisable?" — may be the more useful metric to compare across all nine countries.

### Caveats

The USG 2026 rate bundles whatever non-salary costs (training, supervision, overheads) sit in those USG lines; government payroll costs may differ (Kenya suggests upward). FTE counts are read as FTE-years funded in that year. Cameroon's government commodity series uses the Section 2.2.3 values; Appendix 1 p.24 prints a conflicting cumulative series. All rates are nominal USD as printed in the MoUs.
