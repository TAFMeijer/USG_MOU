"""MoU dashboard — Sources, links & methodology."""
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(page_title="MoU dashboard — Sources & methodology", page_icon="🔗", layout="wide")

st.title("Sources & methodology")

st.markdown(
    "All information in this dashboard is **publicly available**. Amounts for all 34 "
    "signed agreements come from the KFF tracker; detailed budget and indicator tables "
    "were transcribed from the 16 published full MoU texts and verified against the PDFs."
)
st.warning(
    "**Provenance caveat** — the MoUs are government-to-government cooperation documents "
    "that were not originally drafted for publication; the copies used here were placed "
    "in the public domain by third parties (Public Citizen, Health Policy Watch, Think "
    "Global Health). By their own terms the MoUs are not international agreements and "
    "all amounts are plans *subject to the availability of funds* — nothing on this "
    "dashboard represents appropriations, disbursements or current implementation "
    "status, and the published scans may have been amended or superseded since. This is "
    "an independent research reconstruction, not an official product of any government "
    "or organisation."
)

# ---------------- reference trackers ----------------
st.markdown(lib.md("""
**How each text became public.** Sixteen of the 34 signed agreements now have a public full text, and the route matters. Public Citizen marks each one: an **asterisk (\*)** means the U.S. government published the text itself, via its Case Act reporting page; a **caret (^)** means the U.S. government released it only in response to Public Citizen's Freedom of Information Act requests. Five texts carry both markers (Kenya, Mozambique, Nigeria, Ethiopia, Malawi), Uganda alone is Case Act only, and **ten are public solely because of the FOIA litigation** — Rwanda, Liberia, Lesotho, Eswatini, Cameroon, Sierra Leone, Botswana, Madagascar, Côte d'Ivoire and Burundi. Public Citizen sued the State Department over its failure to produce these records; the August 2026 production (FL-2026-00021) is what that suit yielded. Every country row carries its marker in `Disclosure marker` and the route in plain words in `How the text became public`.
"""))

st.subheader("Reference trackers & mirrors")
src = lib.load_sources()
st.dataframe(
    src,
    use_container_width=True,
    hide_index=True,
    column_config={"URL": st.column_config.LinkColumn("URL")},
)

# ---------------- all 34 countries ----------------
st.subheader("All 34 signed MoUs")
st.caption(
    "Click a PDF link to open the source document. 16 countries have a public full text; "
    "a pre-signature draft also exists for South Sudan (see reference table above)."
)
c = lib.load_countries()
st.dataframe(
    c,
    use_container_width=True,
    hide_index=True,
    column_config={
        "MoU PDF URL": st.column_config.LinkColumn("MoU PDF"),
        "Total agreement (USD)": st.column_config.NumberColumn(format="dollar"),
        "USG (USD)": st.column_config.NumberColumn(format="dollar"),
        "Co-financing (USD)": st.column_config.NumberColumn(format="dollar"),
        "USG share": st.column_config.NumberColumn(format="percent"),
    },
)

# ---------------- methodology ----------------
st.subheader("Methodology & caveats")
st.markdown(lib.md(
    """
**Extraction.** Each published MoU PDF was transcribed table by table (budget appendices and
Section-1 indicator tables), then independently verified against the source document. Three
transcription errors were caught and corrected; genuine errors *in the source documents*
(misprinted totals, conflicting appendices) are preserved as printed and flagged in the
`Source note` column of `data/budget_tidy.csv`.

**Printed MoU footnotes.** The footnotes the MoUs themselves print on their funding and
indicator tables — asterisked cells, "Note:" lines, superscript source citations — are
transcribed **verbatim** into the `MoU footnote (verbatim)` column of both tidy tables,
with the exact section/page and marked cells in `MoU footnote location`. Each note is
carried across the **full 2026–2030 line** it qualifies, even where the printed marker sits
on specific cells (e.g. Mozambique's surveillance line: "*Includes funding for surveys
discussed in Section 4.1." — asterisks on 2027 & 2029), so a single-year filter can't miss
a caveat. Liberia's MoU prints no table footnotes. Côte d'Ivoire has one orphan asterisk
(on the "Existing # FTEs Funded" column header) whose note text is missing along with the
scan's appendix pages. The dashboard shows these notes in chart tooltips and under the
affected panels.

**What sums, what doesn't.** Only rows with `Row type = "Line item"` (plus
existing-government rows) are aggregated into `data/budget_series.csv`, which feeds every
chart. Excluded from sums: the MoUs' own subtotal rows, 2026 appendix breakdowns (nested in
line items), domestic-expenditure-increase pledges (a different measure of the same money),
and FTE headcount rows (not dollars).

**Government = new + existing.** Kenya, Uganda, Mozambique, Liberia, Côte d'Ivoire and
Cameroon tabulate *existing* government funding alongside new co-financing; Nigeria,
Ethiopia and Rwanda do not, so their government lines are new co-financing only and their
true shares are **understated**.

**Imputed government $ (dashed lines / sidebar toggle).** Six MoUs commit government
frontline **lab-worker and healthcare-worker FTEs without pricing them**. Where the charts
show government $ for those lines, they are **imputed**: government FTEs × a $/FTE rate
derived from the *same MoU's USG side* (2026 unit rate, flat nominal), or from
peer-country government rates where no in-country rate exists. This is the MoUs' own
convention — Ethiopia's printed government HCW $ equals its USG FTE drawdown × the USG
2026 rate ($1,748) to the dollar, and Kenya's printed government lab rate ($12,548) equals
its USG 2026 rate.

**New vs Existing FTEs.** The FTE tables print a "New" and an "Existing" column, where
*Existing is written from each year's own perspective*: Existing(t) = pre-MoU baseline +
cumulative prior-year new absorptions. A worker absorbed in year t is paid in every later
year, so the imputation funds **new + previously absorbed FTEs each year** (e.g. Cameroon
labs: 62 → 125 → 187 FTEs, i.e. $0.38M → $0.77M → $1.16M). Pre-MoU baseline workforces
(Côte d'Ivoire: 39,800 HCW + 1,900 lab; Uganda: 2,199 lab) are **excluded** — they are
baseline effort, not MoU co-financing. The printed Existing columns are recorded in
`budget_tidy.csv` as `Row type = "Line item - existing (excl. from headline total)"`.

**Uganda: continuation of absorbed cohorts.** Uganda's printed government HRH $ prices
only each year's **new** cohort (the App. 3 national New column — $/new-FTE is a near-flat
$3,581/$3,591/$3,611, rising to $6,337 in 2030 as the cohort mix shifts from CHEWs to
clinical cadres); absorbed cohorts move into the Existing column with their continued
salaries unpriced. The dashboard imputes that continuation (32,222 HCW + 1,086 lab
FTE-years × the own rate) as a separate dashed series. Uganda's cadre-level tables
(7 cadres, App. 3 pp. 30–32) are in `analysis/uganda_cadre_fte.csv`; their New columns
sum to the national table exactly.

Imputed amounts (5-yr): Cameroon $27.7M (HCW + lab, own 2026 rates) · Ethiopia labs $1.1M
(own constant rate) · Mozambique labs $1.4M (own marginal rate, $6,600/FTE) · Rwanda
$14.1M (own 2026 rates; its $ and FTE tables misalign — low confidence) · Uganda $122.8M
(absorbed-cohort continuation, own $3,601 rate) · **Côte d'Ivoire $202.7M (peer rates
only — its MoU prints no HRH $ at all; range $97–268M — treat with caution)**.
Every imputed row is flagged `Row type = "Imputed (derived - not printed in MoU)"` in
`data/budget_tidy.csv` with FTEs, rate and confidence in its Source note; the sidebar /
overview toggle removes them entirely. Full derivation: `analysis/fte_rate_imputation_all.py`
and `analysis/Gov_HRH_imputation_all_countries.md`.

**Pre-MoU baseline workforce (dotted lines / second toggle).** Four MoUs also tabulate the
government's *existing* workforce — the pre-MoU baseline stock in the "Existing # FTEs
Funded" columns: **Uganda 49,014 HCW + 2,199 lab (national 51,213 net of lab) ·
Côte d'Ivoire 39,800 HCW + 1,900 lab · Mozambique 38,462 HCW (App. 3 cadres) · Liberia
6,577 HCW + 538 lab**. Valued at the same rates this is **~$2.65bn over the term**
(Uganda $951M · CIV $775M · Moz $767M · Liberia $156M) — two and a half times the
~$1.07bn of MoU HRH commitments, and the concrete form of the "existing government
funding" the co-funding summaries fold into their headlines. It is shown as its own
dotted series (`Basis = "Imputed baseline (pre-MoU)"`, `Row type = "Imputed baseline
(pre-MoU - derived)"`) precisely so it can be seen *and* filtered out — it is baseline
effort, not MoU co-financing. Kenya, Cameroon, Ethiopia, Rwanda and Nigeria print no
workforce baseline.

The same toggle also removes the **printed existing commodity funding** the MoUs carry
from 2026 (dash-dot lines, `Basis = "Printed in MoU (existing/pre-MoU)"`): each existing
series' 2026 level held flat — **Kenya $540M · Uganda $154M · Côte d'Ivoire $130M ·
Liberia $40M · Mozambique $25M over 2026–30 (~$889M; Kenya's 2031 adds a further
~$108M in the tidy data)**. Growth above the 2026 level (e.g. Uganda's ramps) and
existing series that start at zero (e.g. Cameroon's, which begin in 2029 as absorbed
continuation) are MoU-era commitments and stay in the main series. With the toggle off,
government $ in 2026 reduces to genuine day-one new co-financing — chiefly Nigeria,
whose MoU prints a $344.8M government commitment already in 2026.

**USG 2026-level reference (thin dotted line / third toggle).** There is no separate USG
baseline layer to add: unlike the government side, the USG's funding is fully priced in
every MoU, and its 2026 amount *is* its pre-MoU baseline carried into year one (several
MoUs plan "100% support" in 2026; Rwanda's §2.3.2 states 2026 equals what the USG
"currently funds"). Summing a USG baseline on top of the printed lines would double-count.
Instead the Country view can overlay each panel with the USG's 2026 level held flat — a
counterfactual reference whose gap to the actual USG line is the **planned withdrawal**
the government side is expected to absorb (e.g. Cameroon: $504.6M at 2026-level vs
$399.3M planned = $105.4M / 21% withdrawal). Never added to any total. Known USG
undercounts remain: Kenya's ~$97.9M cost-of-doing-business margin, Nigeria's & Ethiopia's
~6% M&O carve-outs, and Rwanda's Bridge-Plan half of the commodity basket sit outside the
MoU budget lines.

**Strategic assistance / investment detail (panel in the Country view).** The strategic
lines are the largest and least specified amounts in most MoUs (up to $278M in a single
year). A full-document sweep of all sixteen MoUs' §2.6 sections found: **Cameroon** is the
only country with a priced domain × year table (4 domains, §2.6.3 pp.16–17, summing to
its strategic line within print rounding — captured in `budget_tidy.csv` as
appendix-detail rows and shown as a donut). **Côte d'Ivoire** prices 10 named items in
narrative form ("$X per year for N years", §2.6.2 pp.15–18; its 2026 items sum to $45.6M
vs the $47.07M lump — $1.47M unexplained). **Rwanda** prices 5 of 8 named items in
narrative ($5M/yr CBHI, $6.8M E-Buzima, $4.5M HIV integration, $21M vector control, $10M
bio-surveillance). **Nigeria** names 3 strategic objectives plus a 10% (~$208M)
faith-based allocation. **Ethiopia (8 areas), Kenya (5), Mozambique (12), Uganda (7) and
Liberia (5)** name their areas without pricing them (Uganda defers detail to an
implementation plan due 1 April 2026; Liberia prints overlapping 2026-only allocations
that exceed its 2026 lump). All items, prices and page references are in
`data/strategic_areas.csv`; the Country view shows each country's domains beside its
strategic-assistance panel.

**The August 2026 release — seven new texts, and what they change.** Public Citizen published
the State Department's FOIA production on 30 August 2026, taking public full texts from 9 to 16.
Seven countries are new to this dashboard — **Lesotho, Eswatini, Sierra Leone, Botswana,
Madagascar, Malawi and Burundi** — and four earlier texts (Rwanda, Liberia, Cameroon,
Côte d'Ivoire) were re-released from the official production. Every source link now points at the
official release rather than a third-party mirror. Four things in the new batch break patterns the
first nine established:

- **Botswana is a three-year MoU (2026–2028).** Every other published text runs five years. Its
  headline amounts are *not* comparable to the others without adjusting for term length, and its
  government share — 79% of the combined total — is the highest of any MoU.
- **Botswana's U.S. line items do not sum to its own printed totals** in any of its three years
  (−$3.6M over the term). It is the only published MoU where the U.S. side fails to reconcile.
- **Burundi and Côte d'Ivoire itemise the 6% management-and-operations carve-out** as an
  Appendix 1 line. Everywhere else it is an unexplained gap between line items and the printed
  total (Lesotho, Madagascar and Botswana all sit exactly 6% below their headline; Lesotho
  footnotes it explicitly).
- **The government "new funding" tables are mislabelled.** Appendix 1 heads them "total *new*
  planned financial support", but comparing them with the §2.x.3 funding plans shows they carry
  the **Total Government Funding** column — new *plus* existing. This holds across every text
  checked, the original nine included, so the government figures in this dashboard already contain
  both components and existing funding is not added on top.

**Where the published texts disagree with the KFF tracker.** Three of the new texts print
different headline amounts from the tracker this dashboard uses for the other 18 countries:
**Malawi** (MoU: $744.8M U.S. / $55.0M government; KFF: $792M / $143.8M), **Eswatini** (MoU
$192.7M U.S.; KFF $205M) and **Botswana** (MoU $99.6M U.S.; KFF $106M, a difference of exactly
6%). Malawi's government gap of $88.8M is not explained by anything in its text. The MoU figures
are used for the detailed tables; the KFF figures remain in `countries.csv` for cross-country
comparability, and both are visible side by side.

**Signature verification.** All 16 texts were confirmed to be signed finals. The FOIA copies
redact the signatures themselves under exemption (b)(6) — white boxes over the ink — but the
signature blocks, dated place-of-signing lines, names and titles are intact, and in several
(Cameroon, Malawi, Rwanda, Côte d'Ivoire) the strokes overrun the redaction box. **South Sudan
is excluded**: the only available text is a pre-signature April 2026 draft, and the agreement was
signed on 25 June 2026. Four signature dates in the signed texts differ from the tracker dates —
Malawi (13 vs 14 Jan 2026), Botswana (22 vs 23 Dec 2025), Nigeria (19 vs 20 Dec 2025) and
Madagascar (22 Dec, where Public Citizen records "22 or 23") — and are noted per country.

**Known gaps in the sources.**
- Kenya USG excludes a "cost of doing business & audits" margin (~$97.9M over the term).
- Nigeria & Ethiopia USG exclude a ~6% M&O carve-out with no per-year breakdown.
- Rwanda's government worker commitments are expressed in FTEs and never monetised
  (now imputed — see above — at low confidence).
- Côte d'Ivoire's frontline workers are FTE-only, and the available scan is missing its
  appendix pages (25–29); its imputed $ rest entirely on peer-country rates.
- Liberia's own summary and detail tables disagree by $1.19M for 2027 (source error).
- Botswana's U.S. line items miss their printed column totals in all three years; its §2.6.3
  strategic-assistance series also differs from its Appendix 1 row by $3.1M.
- Lesotho's Appendix 1 omits government commodity funding entirely ($16.6M–$24.3M a year,
  recovered here from §2.3.3); its §2.6.3 strategic series is $2.7M below its Appendix 1 row.
- Eswatini's government detail Total row disagrees with its summary table by $99 (2028) and
  $10,000 (2030); Sierra Leone's 2027 government column is $10,000 short of its own line items;
  Malawi's 2028 U.S. column is $809 short; Burundi's 2029 U.S. column is $400 over.
- Madagascar's maternal mortality target *worsens* in the final year (286 in 2029 → 295 in 2030),
  and its net-distribution series swings between 1.7M and 16.7M with no explanatory note.
- Malawi's adult new-HIV-infection target falls to 2027 then rises every year to 2030.

**Reproducibility.** The tidy tables in `data/` are the single source of truth; the charts
never hardcode a number.
"""
))

st.caption(
    "Dashboard data compiled August 2026 from the sources above. "
    "Not an official product of any government or organisation."
)
