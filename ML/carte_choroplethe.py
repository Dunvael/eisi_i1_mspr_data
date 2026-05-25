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


fig = px.choropleth_map(

    df,

    geojson=geojson,

    locations="code_insee",

    featureidkey="properties.code",

    color="classe_politique",

    hover_name="localisation",

    hover_data={

        "code_insee": True,

        "classe_politique": True,

        "taux_chomage": True,

        "population": True,

        "revenu_median_final": True,

        "densite": True
    },

    color_discrete_map={

        "extreme_droite": "#0B1F8C",

        "droite": "#6FA8FF",

        "centre": "#FFD966",

        "gauche": "#6AA84F",

        "extreme_gauche": "#38761D"
    },

    zoom=5,

    center={
        "lat": 46.5,
        "lon": 2.5
    },

    opacity=0.75
)

fig.show()