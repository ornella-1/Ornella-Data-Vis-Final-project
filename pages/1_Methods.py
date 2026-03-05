import streamlit as st

st.set_page_config(page_title="Methods", layout="wide")

st.subheader("Data Source")
st.info("Dataset: [National Database of Childcare Prices](https://github.com/rfordatascience/tidytuesday/blob/main/data/2023/2023-05-09/readme.md).")
st.info("The primary dataset used in this analysis is the county-level childcare cost dataset made publicly available through the TidyTuesday repository. The unit of observation is the county-year level, allowing for both cross-sectional and longitudinal analysis. Each observation corresponds to a specific U.S. county in a given year between 2008 and 2018. The dataset includes detailed measures of weekly childcare prices for different age groups and care types, including center-based and family childcare arrangements. For consistency across counties and years, our primary cost measure focuses on median weekly center-based care for school-age children (mcsa). This variable serves as our central indicator of childcare pricing. To contextualize childcare costs within broader economic conditions, the dataset also includes several socioeconomic indicators derived from the American Community Survey. These include individual poverty rates (pr_p) and female labor force participation rates for individuals aged 20–64 (flfpr_20to64). These variables allow us to examine the relationship between childcare prices, economic vulnerability, and women’s labor supply. In addition, we incorporate a Rural–Urban Continuum Code (RUCC 2023) dataset to classify counties based on their degree of urbanization. Counties are categorized as Urban if their RUCC code is 3 or below and Rural otherwise. This classification enables systematic comparison between predominantly urban and predominantly rural areas.")
st.write("- Variables used: ")




st.write(
    """
II. **Research Question and Methodology**

Our research question can be broken down into three core components:

1. How do childcare costs vary across counties and over time?  
2. What is the relationship between childcare costs and socioeconomic indicators such as poverty and female labor force participation?  
3. Do these relationships differ systematically between rural and urban counties?

By structuring the analysis around these sub-questions, the project aims to connect childcare affordability to broader structural patterns of inequality and labor market participation.

The methodology for this project focused primarily on data cleaning, integration, and panel construction. First, we standardized county identifiers using five-digit Federal Information Processing Standard (FIPS) codes. The childcare dataset, county reference file, RUCC classification data, and geographic shapefiles did not initially share consistent formatting. Some FIPS codes were stored as integers, others as strings, and some lacked leading zeros. We converted all identifiers to zero-padded five-character strings to ensure accurate merging and prevent duplicate or mismatched counties.

Second, we assessed and cleaned missing values across key variables, including childcare costs, poverty rates, and female labor force participation. Non-standard missing entries (e.g., “N/A” or text-based nulls) were standardized and replaced with consistent null values. We examined missingness by year and by state to verify that gaps would not systematically bias comparisons. Observations lacking essential classification information were excluded to preserve consistency.

Third, we merged the childcare dataset with county-level geographic information and the Rural–Urban Continuum Code (RUCC 2023) dataset using FIPS codes. This allowed us to classify counties as Urban (RUCC ≤ 3) or Rural (RUCC > 3). Unmatched counties were reviewed and removed when urbanicity could not be reliably determined.

Finally, we verified panel completeness across the 2008–2018 period and restricted certain comparative analyses to counties or states with full year coverage. After cleaning and validation, we constructed a consistent county-year panel dataset suitable for longitudinal and rural–urban comparison.
"""
)


st.subheader("Preprocessing")
st.write(
    """
For this project, we began by loading several raw datasets: county‑level childcare costs, county metadata, the RUCC rural–urban classification codes, and U.S. county geographic boundaries. Because these sources were created independently, our first task was to make them compatible. We standardized all county FIPS codes into a consistent five‑digit format and used them to derive state identifiers, which allowed us to merge the datasets cleanly.

Once the identifiers were aligned, we combined the childcare cost data with the county‑level demographic information. This produced a unified dataset containing each county’s FIPS code, state name, year, childcare cost, poverty rate, and female labor force participation rate. For the state‑level visualizations, we aggregated these county‑level values to compute state averages—such as average childcare cost and average poverty rate—so that we could compare states directly.

To build the geographic components of the project, we used GeoPandas to process spatial data. We dissolved county geometries into state shapes and merged these boundaries with the aggregated state metrics. This process generated GeoJSON features for each state and year, which we then used to create the interactive choropleth maps.

For the rural–urban analysis, we incorporated RUCC codes to classify each county as either urban or rural. After assigning these classifications, we selected a set of states for deeper comparison and used this enriched dataset to build the interactive county‑level dashboard.

Finally, we calculated a national time series of average childcare costs across all counties and years. This provided a broader view of how childcare prices have changed over time and helped contextualize the more detailed state‑ and county‑level patterns.
"""
)

st.subheader("Limitations")
st.write(
    """
The childcare dataset does not provide full coverage for every county or every year, and missing observations are especially common in rural areas and in states with smaller populations. Because of these gaps, we were unable to construct a complete national panel and instead relied on a sample of counties and states with consistent data availability. As a result, the patterns we observe—particularly in the rural–urban comparisons—reflect this sample rather than the entire United States. The conclusions are therefore not fully generalizable, though they still offer meaningful insight into how childcare costs relate to broader socioeconomic conditions.

Related to this, our project is descriptive rather than causal. The visualizations are designed to help readers recognize patterns and potential relationships between childcare costs, poverty, and women’s labor force participation, but we did not conduct statistical modeling or causal inference. We can identify associations, but we cannot claim that one variable directly causes changes in another.

Finally, our rural–urban classification is based on RUCC codes, which simplify a complex continuum of urbanicity and may not capture local nuance. In addition, some of our state‑level visualizations aggregate county data into statewide averages, which can obscure important within‑state variation and mask local disparities.
"""
)


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
