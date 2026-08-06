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

**What sums, what doesn't.** Only rows with `Row type = "Line item"` (plus
existing-government rows) are aggregated into `data/budget_series.csv`, which feeds every
chart. Excluded from sums: the MoUs' own subtotal rows, 2026 appendix breakdowns (nested in
line items), domestic-expenditure-increase pledges (a different measure of the same money),
and FTE headcount rows (not dollars).

**Government = new + existing.** Kenya, Uganda, Mozambique, Liberia, Côte d'Ivoire and
Cameroon tabulate *existing* government funding alongside new co-financing; Nigeria,
Ethiopia and Rwanda do not, so their government lines are new co-financing only and their
true shares are **understated**.

**Known gaps in the sources.**
- Kenya USG excludes a "cost of doing business & audits" margin (~$97.9M over the term).
- Nigeria & Ethiopia USG exclude a ~6% M&O carve-out with no per-year breakdown.
- Rwanda's government worker commitments are expressed in FTEs and never monetised.
- Côte d'Ivoire's frontline workers are FTE-only, and the available scan is missing its
  appendix pages (25–29).
- Liberia's own summary and detail tables disagree by $1.19M for 2027 (source error).

**Reproducibility.** The tidy tables in `data/` are the single source of truth; the charts
never hardcode a number.
"""
)

st.caption(
    "Dashboard data compiled August 2026 from the sources above. "
    "Not an official product of any government or organisation."
)
