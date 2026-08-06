"""MoU dashboard — Country investment view (small multiples per investment area)."""
import altair as alt
import pandas as pd
import streamlit as st

import mou_lib as lib

st.set_page_config(page_title="MoU dashboard — Country investment view", page_icon="💵",
                   layout="wide")

YEAR_AXIS = alt.Axis(labelAngle=-45, labelFontSize=13, labelFontWeight="bold", title=None)


@st.cache_data
def data():
    return lib.add_share(lib.load_budget_series())


@st.cache_data
def countries_meta():
    return lib.load_countries().set_index("Country")


df = data()
meta = countries_meta()

country = st.sidebar.selectbox("Country", sorted(df["Country"].unique()))
unit = st.sidebar.radio("Unit", ["US$", "% of combined"])
funder_pick = st.sidebar.radio("Funder", ["USG", "Govt (existing + new)", "Both"], index=2)
FUNDER_MAP = {"USG": ["USG"], "Govt (existing + new)": [lib.GOV_LABEL],
              "Both": ["USG", lib.GOV_LABEL]}
funders = FUNDER_MAP[funder_pick]

# ---------------- header with source link ----------------
row = meta.loc[country]
url = row.get("MoU PDF URL", "")
host = row.get("Hosted by", "")
title = f"[{country}]({url})" if isinstance(url, str) and url.startswith("http") else country
st.markdown(f"## {title}")
st.caption(
    f"Signed {row['Signed']} · {row['Doc type']} · "
    + (f"full text hosted by {host} (click the country name to open the PDF) · " if host else "")
    + "all source links on the [Sources & methodology](Sources_and_methodology) page"
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total agreement (KFF)", lib.fmt_usd(row["Total agreement (USD)"]))
k2.metric("USG", lib.fmt_usd(row["USG (USD)"]))
k3.metric("Co-financing", lib.fmt_usd(row["Co-financing (USD)"]))
share = row["USG share"]
k4.metric("USG share (headline)", f"{100 * share:.0f}%" if pd.notna(share) else "–")

# ---------------- small multiples ----------------
m = df[
    (df["Country"] == country)
    & (df["Funder"].isin(funders))
    & (df["Investment area"] != "All areas combined")
]
areas = [a for a in lib.area_options(m) if a != "All areas combined"]

st.markdown(
    f"#### Funding by investment area, 2026–2030 "
    f"({'US$ per year' if unit == 'US$' else 'share of combined USG + government funding'})"
)

funder_scale = alt.Scale(
    domain=["USG", lib.GOV_LABEL], range=[lib.USG_COLOR, lib.GOV_COLOR]
)

cols = st.columns(3)
for i, a in enumerate(areas):
    sub = m[m["Investment area"] == a]
    if sub["Amount"].sum() <= 0:
        continue
    with cols[i % 3]:
        if unit == "US$":
            ch = (
                alt.Chart(sub)
                .mark_line(point=True, strokeWidth=2.5)
                .encode(
                    x=alt.X("Year:O", axis=YEAR_AXIS),
                    y=alt.Y("Amount:Q", title=None, axis=alt.Axis(format="~s")),
                    color=alt.Color("Funder:N", scale=funder_scale, legend=None),
                    tooltip=["Funder", "Year", alt.Tooltip("Amount:Q", format=",.0f")],
                )
                .properties(height=190, title=alt.TitleParams(a, fontSize=13))
            )
            st.altair_chart(ch, use_container_width=True)
        else:
            sub2 = sub.dropna(subset=["Share"])
            if sub2.empty:
                continue
            line = (
                alt.Chart(sub2)
                .mark_line(point=True, strokeWidth=2.5)
                .encode(
                    x=alt.X("Year:O", axis=YEAR_AXIS),
                    y=alt.Y("Share:Q", title=None, axis=alt.Axis(format=".0%"),
                            scale=alt.Scale(domain=[0, 1])),
                    color=alt.Color("Funder:N", scale=funder_scale, legend=None),
                    tooltip=["Funder", "Year", alt.Tooltip("Share:Q", format=".0%"),
                             alt.Tooltip("Amount:Q", format=",.0f")],
                )
                .properties(height=190, title=alt.TitleParams(a, fontSize=13))
            )
            rule = (
                alt.Chart(pd.DataFrame({"y": [0.5]}))
                .mark_rule(strokeDash=[4, 4], color="#898781")
                .encode(y="y:Q")
            )
            st.altair_chart(line + rule, use_container_width=True)

st.markdown(
    f'<span style="color:{lib.USG_COLOR};font-weight:600">— USG</span> &nbsp; '
    f'<span style="color:{lib.GOV_COLOR};font-weight:600">— Govt (existing + new)</span>',
    unsafe_allow_html=True,
)

# ---------------- detail table ----------------
with st.expander("Line-item detail (as printed in the MoU, with caveats)"):
    tidy = lib.load_budget_tidy()
    detail = tidy[tidy["Country"] == country]
    st.dataframe(
        detail,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Source (MoU PDF)": st.column_config.LinkColumn("Source (MoU PDF)",
                                                            display_text="open PDF")
        },
    )
    st.caption(
        "Only rows with Row type = 'Line item' (plus existing-government rows) feed the "
        "charts above; other row types are excluded to avoid double counting."
    )
