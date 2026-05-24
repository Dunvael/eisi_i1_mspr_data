import pandas as pd
import plotly.express as px
import json


df = pd.read_csv(
    "data_cleaned/2022/Z_dataframe_final_ml.csv",
    sep=";",
    dtype={"code_insee": str}
)

with open(
    "data_raw/2022_raw/referentiels/communes.geojson",
    "r",
    encoding="utf-8"
) as f:

    geojson = json.load(f)


fig = px.choropleth_mapbox(
    df,

    geojson=geojson,

    locations="code_insee",

    featureidkey="properties.code",

    color="classe_politique",

    hover_name="localisation",

    mapbox_style="carto-positron",

    zoom=5,

    center={
        "lat": 46.5,
        "lon": 2.5
    },

    opacity=0.7
)

fig.show()