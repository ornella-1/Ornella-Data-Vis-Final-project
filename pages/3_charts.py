import altair as alt
import pandas as pd


def make_cost_trend_line(cost_trend: pd.DataFrame) -> alt.Chart:
    """
    Line chart of national average childcare cost over time with 2008–2010 band.
    """
    base = alt.Chart(cost_trend).encode(
        x=alt.X("study_year:O", title="Year"),
        y=alt.Y("mcsa:Q", title="Average weekly childcare cost (mcsa)"),
    )

    line = base.mark_line(point=True, color="#1f77b4")

    band = (
        alt.Chart(cost_trend)
        .mark_rect(color="#d62728", opacity=0.15)
        .encode(
            x=alt.X("2008:O", title=""),
            x2="2010:O",
        )
    )

    return (band + line).properties(width=500, height=300, title="National Average Childcare Cost (2008–2018)")


def make_sliding_choropleth_maps(geo_features, state_metrics):
    import altair as alt

    geo_data = alt.Data(values=geo_features)
    years = sorted(state_metrics["study_year"].unique())

    year_slider = alt.binding_range(
        min=int(min(years)),
        max=int(max(years)),
        step=1,
        name="Year: "
    )
    year_selection = alt.param(
        name="selected_year",
        value=int(min(years)),
        bind=year_slider
    )

    # Childcare cost
    childcare_chart = (
        alt.Chart(geo_data)
        .mark_geoshape(stroke="white", strokeWidth=0.5)
        .transform_filter("toNumber(datum.properties.study_year) == selected_year")
        .encode(
            color=alt.Color(
                "properties.mcsa_mean:Q",
                scale=alt.Scale(
                    scheme="blues",
                    domain=[
                        float(state_metrics["mcsa_mean"].min()),
                        float(state_metrics["mcsa_mean"].max()),
                    ],
                ),
                title="Avg childcare cost",
            ),
            tooltip=[
                alt.Tooltip("properties.state_name:N", title="State"),
                alt.Tooltip("properties.mcsa_mean:Q", title="Childcare cost", format=".2f"),
                alt.Tooltip("properties.study_year:Q", title="Year"),
            ],
        )
        .project("albersUsa")
        .properties(width=450, height=280)
    )

    # Poverty
    poverty_chart = (
        alt.Chart(geo_data)
        .mark_geoshape(stroke="white", strokeWidth=0.5)
        .transform_filter("toNumber(datum.properties.study_year) == selected_year")
        .encode(
            color=alt.Color(
                "properties.pr_f_mean:Q",
                scale=alt.Scale(
                    scheme="oranges",
                    domain=[
                        float(state_metrics["pr_f_mean"].min()),
                        float(state_metrics["pr_f_mean"].max()),
                    ],
                ),
                title="Family poverty rate",
            ),
            tooltip=[
                alt.Tooltip("properties.state_name:N", title="State"),
                alt.Tooltip("properties.pr_f_mean:Q", title="Poverty rate", format=".2f"),
                alt.Tooltip("properties.study_year:Q", title="Year"),
            ],
        )
        .project("albersUsa")
        .properties(width=450, height=280)
    )

    # Female LFPR
    labor_chart = (
        alt.Chart(geo_data)
        .mark_geoshape(stroke="white", strokeWidth=0.5)
        .transform_filter("toNumber(datum.properties.study_year) == selected_year")
        .encode(
            color=alt.Color(
                "properties.flfpr_20to64_mean:Q",
                scale=alt.Scale(
                    scheme="purples",
                    domain=[
                        float(state_metrics["flfpr_20to64_mean"].min()),
                        float(state_metrics["flfpr_20to64_mean"].max()),
                    ],
                ),
                title="Female LFPR (20–64)",
            ),
            tooltip=[
                alt.Tooltip("properties.state_name:N", title="State"),
                alt.Tooltip("properties.flfpr_20to64_mean:Q", title="LFPR", format=".2f"),
                alt.Tooltip("properties.study_year:Q", title="Year"),
            ],
        )
        .project("albersUsa")
        .properties(width=500, height=300)
    )

    bottom_row = (
        alt.hconcat(labor_chart, poverty_chart)
        .add_params(year_selection)
        .resolve_scale(color="independent")
    )

    combined = (
        alt.vconcat(childcare_chart, bottom_row)
        .add_params(year_selection)
        .resolve_scale(color="independent")
        .properties(title="Childcare Cost, Female LFPR & Poverty Rate by State")
    )

    return combined


def make_urban_rural_state_maps(county_avg: pd.DataFrame, geo_counties_raw: dict, sample_states: list) -> alt.Chart:
    """
    County-level map for 8 sample states, colored by childcare cost and faceted by state.
    """
    feats = geo_counties_raw["features"]
    geo_data = alt.Data(values=feats)

    county_avg = county_avg.copy()
    county_avg["county_fips_code"] = county_avg["county_fips_code"].astype(str).str.zfill(5)

    lookup = alt.LookupData(
        county_avg,
        key="county_fips_code",
        fields=["state_name", "mcsa", "pr_p", "flfpr_20to64", "urbanicity_rucc"],
    )

    chart = (
        alt.Chart(geo_data)
        .mark_geoshape(stroke="white", strokeWidth=0.2)
        .transform_lookup(
            lookup="properties.fips5",
            from_=lookup,
        )
        .transform_filter(
            alt.FieldOneOfPredicate(field="state_name", oneOf=sample_states)
        )
        .encode(
            color=alt.Color(
                "mcsa:Q",
                title="Avg childcare cost",
                scale=alt.Scale(scheme="blues"),
            ),
            tooltip=[
                alt.Tooltip("properties.NAME:N", title="County"),
                alt.Tooltip("state_name:N", title="State"),
                alt.Tooltip("mcsa:Q", title="Childcare cost", format=".2f"),
                alt.Tooltip("pr_p:Q", title="Poverty rate", format=".2f"),
                alt.Tooltip("flfpr_20to64:Q", title="Female LFPR", format=".2f"),
                alt.Tooltip("urbanicity_rucc:N", title="Urbanicity"),
            ],
            facet=alt.Facet("state_name:N", columns=4, title=None),
        )
        .project("albersUsa")
        .properties(width=150, height=120)
    )

    return chart


def make_heatmap_stacked(county_avg: pd.DataFrame) -> alt.VConcatChart:
    """
    Two heatmaps: mcsa vs pr_p and mcsa vs flfpr_20to64, colored by count,
    with regression lines by urbanicity_rucc.
    """
    df = county_avg.copy()

    base = alt.Chart(df).transform_filter("datum.mcsa != null")

    # Cost vs poverty
    heat_pov = (
        base.mark_rect()
        .encode(
            x=alt.X("mcsa:Q", bin=alt.Bin(maxbins=20), title="Childcare cost"),
            y=alt.Y("pr_p:Q", bin=alt.Bin(maxbins=20), title="Family poverty rate"),
            color=alt.Color("count():Q", scale=alt.Scale(scheme="blues"), title="Count"),
        )
        .properties(width=400, height=200, title="Cost vs family poverty rate")
    )

    reg_pov = (
        base.mark_line(color="black")
        .encode(
            x="mcsa:Q",
            y="pr_p:Q",
            detail="urbanicity_rucc:N",
        )
    )

    top = heat_pov + reg_pov

    # Cost vs female LFPR
    heat_lfpr = (
        base.mark_rect()
        .encode(
            x=alt.X("mcsa:Q", bin=alt.Bin(maxbins=20), title="Childcare cost"),
            y=alt.Y("flfpr_20to64:Q", bin=alt.Bin(maxbins=20), title="Female LFPR (20–64)"),
            color=alt.Color("count():Q", scale=alt.Scale(scheme="greens"), title="Count"),
        )
        .properties(width=400, height=200, title="Cost vs female LFPR (20–64)")
    )

    reg_lfpr = (
        base.mark_line(color="black")
        .encode(
            x="mcsa:Q",
            y="flfpr_20to64:Q",
            detail="urbanicity_rucc:N",
        )
    )

    bottom = heat_lfpr + reg_lfpr

    return alt.vconcat(top, bottom).resolve_scale(color="independent")


def make_county_dashboard(geo_merged):
    # Accept GeoDataFrame directly
    data = geo_merged

    years = sorted(data["study_year"].unique())
    states = sorted(data["state_name"].unique())

    year_param = alt.param(
        name="year",
        value=min(years),
        bind=alt.binding_range(min=min(years), max=max(years), step=1, name="Year: ")
    )

    state_param = alt.param(
        name="state",
        value=states[0],
        bind=alt.binding_select(options=states, name="State: ")
    )

    county_select = alt.selection_point(fields=["county_fips_code"])

    # Map
    map_chart = (
        alt.Chart(data)
        .mark_geoshape(stroke="#333", strokeWidth=0.4)
        .transform_filter("datum.state_name == state")
        .transform_filter("datum.study_year == year")
        .encode(
            color=alt.Color("mcsa:Q", title="Childcare cost"),
            tooltip=[
                "state_name:N",
                "county_name:N",
                alt.Tooltip("mcsa:Q", format=",.0f"),
                alt.Tooltip("pr_p:Q", format=".1f"),
                alt.Tooltip("flfpr_20to64:Q", format=".1f"),
            ],
            opacity=alt.condition(county_select, alt.value(1), alt.value(0.5)),
        )
        .add_params(year_param, state_param, county_select)
        .project("albersUsa")
        .properties(width=700, height=600)
    )

    # Scatter
    scatter = (
        alt.Chart(data)
        .mark_circle(size=70)
        .transform_filter("datum.state_name == state")
        .transform_filter("datum.study_year == year")
        .encode(
            x=alt.X("mcsa:Q", title="Childcare cost"),
            y=alt.Y("pr_p:Q", title="Poverty rate"),
            tooltip=[
                "state_name:N",
                "county_name:N",
                alt.Tooltip("mcsa:Q", format=",.0f"),
                alt.Tooltip("pr_p:Q", format=".1f"),
            ],
            opacity=alt.condition(county_select, alt.value(1), alt.value(0.6)),
        )
        .add_params(county_select)
        .properties(width=350, height=300)
    )

    # LFPR bar chart
    lfpr_base = (
        alt.Chart(data)
        .transform_filter("datum.state_name == state")
        .transform_filter("datum.study_year == year")
    )

    county_bar = (
        lfpr_base
        .transform_filter(county_select)
        .transform_calculate(label='"Selected county"')
        .mark_bar()
        .encode(
            x="label:N",
            y=alt.Y("flfpr_20to64:Q", title="Female LFPR (20–64)")
        )
    )

    state_bar = (
        lfpr_base
        .transform_aggregate(
            state_avg="mean(flfpr_20to64)",
            groupby=["state_name"]
        )
        .transform_calculate(label='"State average"')
        .mark_bar(color="orange")
        .encode(
            x="label:N",
            y="state_avg:Q"
        )
    )

    lfpr_chart = (county_bar + state_bar).properties(width=350, height=200)

    return alt.hconcat(
        map_chart,
        alt.vconcat(scatter, lfpr_chart)
    ).resolve_scale(color="shared")