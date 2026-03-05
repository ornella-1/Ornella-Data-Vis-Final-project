import streamlit as st

st.set_page_config(page_title="Methods", layout="wide")

st.title("Methods & Limitations")

st.subheader("Data Source")
st.info("Dataset: [National Database of Childcare Prices](https://github.com/rfordatascience/tidytuesday/blob/main/data/2023/2023-05-09/readme.md).")
st.info("")
st.write("- Variables used: ")


st.subheader("Preprocessing")
st.write("")
st.write("")
st.write("")

st.subheader("Transformations")
st.write("")
st.write("")
st.write("")

st.subheader("Limitations")
st.write("")


import streamlit as st
from utils import data_io as io
import charts

st.set_page_config(page_title="Methods", layout="wide")

st.title("Methods")

@st.cache_data(show_spinner="Loading and preprocessing data…")
def get_data():
    return io.load_and_preprocess_all(
        childcare_path="./data/childcare_costs.csv",
        counties_path="./data/counties.csv",
        rucc_path="./data/Ruralurbancontinuumcodes2023.csv",
        geojson_path="./data/geojson-counties-fips.json",
    )

data = get_data()

st.markdown(
    """
### Data sources

- National Database of Childcare Prices (county-level childcare costs)
- County demographic data
- USDA Rural–Urban Continuum Codes (2023)
- US county GeoJSON boundaries

### Preprocessing pipeline

1. Normalize all county FIPS codes to 5 digits.
2. Derive `state_id` from county FIPS.
3. Merge childcare and county data at the county level.
4. Compute state-level metrics by year:
   - `mcsa_mean` – average weekly center-based childcare cost
   - `pr_f_mean` – average family poverty rate
   - `flfpr_20to64_mean` – female labor-force participation (20–64)
5. Dissolve county geometries to state geometries.
6. Attach metrics to each state geometry for each study year.
7. Attach RUCC codes and derive an Urban/Rural label.
8. Build county- and state-level summaries for an 8-state rural/urban sample.
"""
)

st.subheader("Example: state-level childcare cost map")

example_choropleth = charts.make_sliding_choropleth_maps(
    data["geo_features"], data["state_metrics"]
)
st.altair_chart(example_choropleth, use_container_width=True)