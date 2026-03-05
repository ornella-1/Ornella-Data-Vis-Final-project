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
