"""MoU dashboard — Full data tables.

Everything, in one place: the complete tidy budget and programmatic tables across
all 9 countries — sortable (click any column header), searchable (filters here
plus the 🔍 icon in each table's toolbar), and downloadable as CSV.
"""
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(page_title="MoU dashboard — Full data tables", page_icon="🗂️",
                   layout="wide")

st.title("Full data tables")
st.caption(
    "The complete extracted datasets behind every chart. Empty filters mean 'show all'. "
    "Click a column header to sort; the 🔍 icon in the table toolbar does a live "
    "full-text search; the ⬇ icon downloads the current view. Definitions and summing "
    "rules are on the [Sources & methodology](Sources_and_methodology) page."
)

tab_budget, tab_prog = st.tabs(["💵 Budget ($ amounts)", "📈 Programmatic data"])

# ================= Budget =================
with tab_budget:
    b = lib.load_budget_tidy()

    f1, f2, f3 = st.columns([2, 2, 1.4])
    with f1:
        f_country = st.multiselect("Country", sorted(b["Country"].unique()),
                                   placeholder="All countries", key="b_country")
    with f2:
        f_area = st.multiselect("Investment area", sorted(b["Investment area"].unique()),
                                placeholder="All areas", key="b_area")
    with f3:
        f_funder = st.multiselect("Funder", sorted(b["Funder"].unique()),
                                  placeholder="All funders", key="b_funder")
    f4, f5, f6 = st.columns([2, 1.4, 2.4])
    with f4:
        f_rowtype = st.multiselect("Row type", sorted(b["Row type"].unique()),
                                   placeholder="All row types", key="b_rowtype")
    with f5:
        f_unit = st.multiselect("Unit", sorted(b["Unit"].unique()),
                                placeholder="All units", key="b_unit")
    with f6:
        f_text = st.text_input("Search category / notes", "", key="b_text",
                               placeholder="e.g. ARV, buffer, surveillance…")

    if f_country:
        b = b[b["Country"].isin(f_country)]
    if f_area:
        b = b[b["Investment area"].isin(f_area)]
    if f_funder:
        b = b[b["Funder"].isin(f_funder)]
    if f_rowtype:
        b = b[b["Row type"].isin(f_rowtype)]
    if f_unit:
        b = b[b["Unit"].isin(f_unit)]
    if f_text:
        mask = (
            b["Category (as printed in MoU)"].str.contains(f_text, case=False, na=False)
            | b["Source note"].astype(str).str.contains(f_text, case=False, na=False)
            | b[lib.FOOTNOTE_COL].astype(str).str.contains(f_text, case=False, na=False)
        )
        b = b[mask]

    st.dataframe(
        b,
        use_container_width=True,
        hide_index=True,
        height=560,
        column_config={
            "Amount": st.column_config.NumberColumn(format="localized"),
            "Source (MoU PDF)": st.column_config.LinkColumn("Source (MoU PDF)",
                                                            display_text="open PDF"),
        },
    )
    c1, c2 = st.columns([1, 3])
    with c1:
        st.download_button(
            "Download full budget table (CSV)",
            (lib.DATA / "budget_tidy.csv").read_bytes(),
            file_name="budget_tidy.csv",
            mime="text/csv",
            key="b_dl",
        )
    with c2:
        st.caption(
            f"{len(b):,} rows shown. To sum money safely: filter Unit = USD and "
            "Row type = 'Line item' (plus the existing-government rows) — the MoUs' own "
            "subtotals, appendix breakdowns and expenditure pledges are flagged so they "
            "don't double-count. 'MoU footnote (verbatim)' = notes printed in the MoU "
            "itself, carried across the full 5-year line; 'MoU footnote location' "
            "pinpoints the marked cells."
        )

# ================= Programmatic =================
with tab_prog:
    p = lib.load_programmatic()

    g1, g2, g3 = st.columns([2, 2, 1.6])
    with g1:
        g_country = st.multiselect("Country", sorted(p["Country"].unique()),
                                   placeholder="All countries", key="p_country")
    with g2:
        g_area = st.multiselect("Programmatic area", sorted(p["Programmatic area"].unique()),
                                placeholder="All areas", key="p_area")
    with g3:
        g_mtype = st.multiselect("Metric type", sorted(p["Metric type"].unique()),
                                 placeholder="All types", key="p_mtype")
    g4, g5, g6 = st.columns([1.6, 1.6, 2.4])
    with g4:
        g_vtype = st.multiselect("Value type", sorted(p["Value type"].unique()),
                                 placeholder="All value types", key="p_vtype")
    with g5:
        g_year = st.multiselect("Year", ["Baseline", "2026", "2027", "2028", "2029", "2030"],
                                placeholder="All years", key="p_year")
    with g6:
        g_text = st.text_input("Search indicator", "", key="p_text",
                               placeholder="e.g. ART, measles, ANC, mortality…")

    if g_country:
        p = p[p["Country"].isin(g_country)]
    if g_area:
        p = p[p["Programmatic area"].isin(g_area)]
    if g_mtype:
        p = p[p["Metric type"].isin(g_mtype)]
    if g_vtype:
        p = p[p["Value type"].isin(g_vtype)]
    if g_year:
        p = p[p["Year"].isin(g_year)]
    if g_text:
        mask = (
            p["Indicator"].str.contains(g_text, case=False, na=False)
            | p[lib.FOOTNOTE_COL].astype(str).str.contains(g_text, case=False, na=False)
        )
        p = p[mask]

    st.dataframe(
        p,
        use_container_width=True,
        hide_index=True,
        height=560,
        column_config={
            "Value": st.column_config.NumberColumn(format="localized"),
            "Source (MoU PDF)": st.column_config.LinkColumn("Source (MoU PDF)",
                                                            display_text="open PDF"),
        },
    )
    c1, c2 = st.columns([1, 3])
    with c1:
        st.download_button(
            "Download full programmatic table (CSV)",
            (lib.DATA / "programmatic_tidy.csv").read_bytes(),
            file_name="programmatic_tidy.csv",
            mime="text/csv",
            key="p_dl",
        )
    with c2:
        st.caption(
            f"{len(p):,} rows shown. Values are as printed in each MoU "
            "(percentages stored as 95 = 95%); check 'Unit / source note' for "
            "inequality-coded targets ('>95%') and baseline years before comparing "
            "across countries. 'MoU footnote (verbatim)' = notes printed in the MoU's "
            "own indicator tables (source citations, baseline caveats, revision "
            "clauses), carried across every year of the affected indicator."
        )
