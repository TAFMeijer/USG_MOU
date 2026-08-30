# USG MoU dashboard

**Live app:** https://usg-mou.streamlit.app/ · **Standalone explorer:** https://tafmeijer.github.io/USG_MOU/

![USG MoU dashboard — funding trajectories and 5-year totals by country](assets/screenshot.png)


Interactive dashboard tracking the **America First Global Health Strategy bilateral health
MoUs** (34 countries, five-year cooperation plans 2026–2030): who funds what, how U.S.
funding tapers while government co-financing ramps up, and the programmatic targets each
agreement commits to.

All information here is **publicly available** — amounts from the
[KFF tracker](https://www.kff.org/global-health-policy/kff-tracker-america-first-mou-bilateral-global-health-agreements/),
detailed tables transcribed from the 9 published full MoU texts hosted by
[Public Citizen](https://www.citizen.org/article/u-s-bilateral-health-agreements-case-act-reporting/),
[Health Policy Watch](https://healthpolicy-watch.news/) and
[Think Global Health](https://www.thinkglobalhealth.org/article/tracking-the-america-first-bilateral-health-agreements).

## Pages

| Page | What it shows |
|---|---|
| **Home (Overview)** | All countries side by side, per investment area — yearly trajectories and 5-year totals, with a **US$ ↔ % of combined** toggle |
| **Country investment view** | One country's small multiples across every investment area, with a USG / Govt (existing + new) / Both toggle and the same $/% toggle; the country name links to the source PDF |
| **Country programmatic view (v0)** | One country's indicator baselines & 2026–2030 targets (outcome / process / 7-1-7), each indicator as its own small chart |
| **Full data tables** | The complete budget and programmatic datasets across all countries — filterable, sortable, searchable, downloadable |
| **Sources & methodology** | Every link (trackers, mirrors, all 34 agreements), extraction method, and caveats |

`explorer.html` is a standalone, dependency-free version of the trajectory explorer —
open it directly in a browser, no Python needed.

## Theming

The app ships light **and** dark themes (`.streamlit/config.toml`); Streamlit's default
setting ("Use system setting") follows the browser/OS colour-scheme preference, and users
can still override it in the app menu. Explicit chart colours track the active theme via
`mou_lib.palette()` (`st.context.theme`), so donut strokes, centre labels, chip legends and
the handful of dark-adjusted series colours switch with it.

## Run locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## Publish

1. Push this folder to a public GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "USG MoU dashboard"
   git branch -M main
   git remote add origin https://github.com/<you>/mou-dashboard.git
   git push -u origin main
   ```
2. Deploy free on [Streamlit Community Cloud](https://share.streamlit.io): *New app* →
   pick the repo → main file `Home.py`. Every push to `main` redeploys automatically.

## Data

| File | Contents |
|---|---|
| `data/budget_series.csv` | Aggregated, safely summable series (Country × Investment area × Year × Funder) — feeds all budget charts |
| `data/budget_tidy.csv` | Full line-item detail as printed in each MoU, with `Row type` flags (subtotals, appendix breakdowns, existing funding), source notes, and the MoUs' own printed footnotes transcribed verbatim (`MoU footnote (verbatim)` / `MoU footnote location`) |
| `data/programmatic_tidy.csv` | Every Section-1 indicator: baseline + yearly targets, units, value types, source notes, and the MoUs' own printed footnotes (verbatim + location) |
| `data/countries.csv` | All 34 agreements: amounts, dates, program areas, source-PDF links |
| `data/sources.csv` | Reference trackers and mirrors |
| `data/strategic_areas.csv` | Strategic-investment domains/areas named in every MoU's §2.6, with printed prices and page references |
| `analysis/` | Derived analyses: $/FTE imputation scripts and outputs, cadre-table harvests (Mozambique, Uganda), baseline valuations, analysis notes |

**Summing rules** (see Sources & methodology page in the app): only `Row type = "Line item"`
rows plus existing-government rows are summed; the MoUs' own subtotals, nested appendix
breakdowns, FTE headcounts and domestic-expenditure pledges are excluded to avoid double
counting. "Government" = new co-financing **plus** existing funding where tabulated
(Nigeria, Ethiopia, Rwanda publish no existing split — their shares are understated).

## Provenance & caveats

**Read this before using the data.** All figures were transcribed from copies of the nine
signed MoU texts that were placed in the public domain by third parties (Public Citizen,
Health Policy Watch, Think Global Health) and from the KFF tracker. The MoUs are
government-to-government cooperation documents that were **not originally drafted for
publication**; no official consolidated dataset of them exists, and this repository is an
independent research reconstruction. In particular:

1. **Amounts are plans, not obligations.** By the MoUs' own terms they are not
   international agreements and all activities are *subject to the availability of funds*.
   Nothing here represents appropriations, disbursements, or current implementation status,
   and the published scans may have been amended or superseded since.
2. **Figures are transcribed as printed**, including source-document errors (misprinted
   totals, conflicting appendices, internally inconsistent tables). These are preserved
   uncorrected and flagged in the `Source note` column.
3. **Derived values are clearly separated from printed ones.** Rows flagged
   `Imputed (derived - not printed in MoU)` / `Imputed baseline (pre-MoU - derived)` and
   series with `Basis` other than "Printed in MoU" are estimates produced by this
   project's documented methodology (FTE commitments priced at unit rates derived from
   the same documents) — they are never printed values, they carry stated confidence
   ranges, and every chart lets you toggle them off. See the app's *Sources &
   methodology* page and `analysis/` for full derivations.
4. Tables were machine-transcribed from the source PDFs and independently verified
   against them. Compiled August 2026. **Not an official product of any government or
   organisation**, and no affiliation with any party to the MoUs is implied. Content is
   provided as-is for research and transparency purposes; corrections are welcome via
   issues or pull requests.

## License

Code and derived data are released under the [MIT License](LICENSE). The underlying MoU
texts remain the work of their authors; transcription here is for research and
transparency purposes.
