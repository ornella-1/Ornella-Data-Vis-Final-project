import streamlit as st
from utils import data_io as io
import charts

GEOJSON_URL = (
    "https://raw.githubusercontent.com/srusti-d/childcare-cost-streamlit/main/data/"
    "geojson-counties-fips.json"
)

st.set_page_config(page_title="Explore Childcare Cost Analysis", layout="wide")

@st.cache_data(show_spinner="Loading and preprocessing data…")
def get_data():
    return io.load_and_preprocess_all(
        childcare_path="./data/childcare_costs.csv",
        counties_path="./data/counties.csv",
        rucc_path="./data/Ruralurbancontinuumcodes2023.csv",
        geojson_path="./data/geojson-counties-fips.json",
    )

if "data" not in st.session_state:
    st.session_state["data"] = get_data()

data = st.session_state["data"]

st.title("Exploring U.S. Childcare Costs (2008–2018)")
st.markdown(
    """
This page walks through five visualisations that together tell the story of
how childcare costs relate to poverty, female labour-force participation,
and geography across the United States over a decade.
Many of these plots are interactive.
"""
)

st.divider()

# 1. National average childcare cost trend
st.header("National Average Childcare Cost Over Time")
st.markdown(
    """
The line below tracks the **national average weekly center-based childcare
cost (mcsa)** from 2008 to 2018. The shaded band marks the 2008–2010
financial-crisis window. Hover over any point to see the exact value.
"""
)

cost_chart = charts.make_cost_trend_line(data["cost_trend"])
st.altair_chart(cost_chart, use_container_width=False)

st.divider()

# 2. State-level choropleth maps with year slider
st.header("Childcare Cost, Female LFPR & Poverty Rate by State")
st.markdown(
    """
Use the **Year** slider to step through each study year and compare how
three state-level metrics change together:

* Center-based childcare cost  
* Female labor-force participation rate (20–64)  
* Family poverty rate  
"""
)

choropleth = charts.make_sliding_choropleth_maps(
    data["geo_features"],
    data["state_metrics"],
)
st.altair_chart(choropleth, use_container_width=False)

st.divider()

# 3. Urban vs rural county classification maps
st.header("Urban vs Rural Counties — 8 State Sample")
st.markdown(
    """
Counties are classified as **Urban** (USDA RUCC code ≤ 3) or **Rural**
(code ≥ 4) using the 2023 Rural-Urban Continuum Codes. The sample covers
four predominantly urban states (Massachusetts, California, Arizona, Delaware)
and four predominantly rural states (North Dakota, Kansas, Oklahoma, Vermont).
Hover over any county to see its average childcare cost, poverty rate, and
female labor-force participation rate.
"""
)

urb_rural = charts.make_urban_rural_state_maps(
    data["county_avg"],
    data["geo_counties_raw"],
    data["sample_states"],
)
st.altair_chart(urb_rural, use_container_width=False)

st.divider()

# 4. Density heatmaps (poverty + LFPR)
st.header("Childcare Cost vs Poverty Rate & Female LFPR")
st.markdown(
    """
Each colored bin in the heatmap shows how many counties fall into that
cost vs predictor bin. Overlaid regression lines show whether the
**Urban** and **Rural** trends differ in slope or direction.

**Top chart** — childcare cost vs family poverty rate  
**Bottom chart** — childcare cost vs female labor-force participation rate  
"""
)

heatmaps = charts.make_heatmap_stacked(data["county_avg"])
st.altair_chart(heatmaps, use_container_width=False)

st.divider()

# 5. Interactive county-level dashboard
st.header("Interactive County-Level Dashboard")
st.markdown(
    """
This dashboard lets you zoom in from the national picture down to individual
states and counties.

1. Choose a **year** and **state**.
2. Hover over each county in the map to see childcare cost, poverty, and LFPR.
3. Use the scatterplot to compare counties within the selected state.
"""
)

dashboard = charts.make_county_dashboard(data["geo_merged_json"])
st.altair_chart(dashboard, use_container_width=False)