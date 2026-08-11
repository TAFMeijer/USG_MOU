"""MoU dashboard — Sources, links & methodology."""
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(page_title="MoU dashboard — Sources & methodology", page_icon="🔗", layout="wide")

st.title("Sources & methodology")

st.markdown(
    "All information in this dashboard is **publicly available**. Amounts for all 34 "
    "signed agreements come from the KFF tracker; detailed budget and indicator tables "
    "were transcribed from the 9 published full MoU texts and verified against the PDFs."
)

# ---------------- reference trackers ----------------
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
    "Click a PDF link to open the source document. 9 countries have a public full text; "
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
st.markdown(
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

Imputed amounts (5-yr): Cameroon $27.7M (HCW + lab, own 2026 rates) · Ethiopia labs $1.1M
(own constant rate) · Mozambique labs $1.4M (own marginal rate, $6,600/FTE) · Rwanda
$14.1M (own 2026 rates; its $ and FTE tables misalign — low confidence) · Uganda labs
$8.0M (peer rate, wage-adjusted) · **Côte d'Ivoire $190.6M (peer rates only — its MoU
prints no HRH $ at all; range $97–268M — treat with caution)**.
Every imputed row is flagged `Row type = "Imputed (derived - not printed in MoU)"` in
`data/budget_tidy.csv` with FTEs, rate and confidence in its Source note; the sidebar /
overview toggle removes them entirely. Full derivation: `analysis/fte_rate_imputation_all.py`
and `analysis/Gov_HRH_imputation_all_countries.md`.

**Known gaps in the sources.**
- Kenya USG excludes a "cost of doing business & audits" margin (~$97.9M over the term).
- Nigeria & Ethiopia USG exclude a ~6% M&O carve-out with no per-year breakdown.
- Rwanda's government worker commitments are expressed in FTEs and never monetised
  (now imputed — see above — at low confidence).
- Côte d'Ivoire's frontline workers are FTE-only, and the available scan is missing its
  appendix pages (25–29); its imputed $ rest entirely on peer-country rates.
- Liberia's own summary and detail tables disagree by $1.19M for 2027 (source error).

**Reproducibility.** The tidy tables in `data/` are the single source of truth; the charts
never hardcode a number.
"""
)

st.caption(
    "Dashboard data compiled August 2026 from the sources above. "
    "Not an official product of any government or organisation."
)
