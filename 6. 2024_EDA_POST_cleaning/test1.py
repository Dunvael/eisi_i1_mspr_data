import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os


# PALETTE COULEURS

BLUE = "#1f77b4"
GRAY = "#7f7f7f"


# 1. CONFIGURATION PAGE

st.set_page_config(
    page_title="Population & Densité 2024",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Analyse Exploratoire : Population & Densité 2024")
st.markdown("Dashboard interactif avec traitement des valeurs extrêmes.")


# 2. CHARGEMENT DES DONNÉES

@st.cache_data
def load_data():
    file_path = "data_cleaned/2024/01_Densite_population/01.3_population_densite_2024_clean.csv"
    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path, sep=";", dtype={"code_insee_2024": str})

    df["Département"] = df["code_insee_2024"].astype(str).str[:2]

    df["population"] = pd.to_numeric(df["population"], errors='coerce')
    df["superficie_km2"] = pd.to_numeric(df["superficie_km2"], errors='coerce')
    df["densite"] = pd.to_numeric(df["densite"], errors='coerce')

    return df

df = load_data()

if df is None:
    st.error("Fichier introuvable. Vérifie le chemin du fichier 01.3.")
    st.stop()

colonnes_analyse = ["population", "superficie_km2", "densite"]


# 3. SIDEBAR - FILTRES

with st.sidebar:
    st.header("Filtres Géographiques")

    departements = sorted(df["Département"].dropna().unique().tolist())
    dep_choisi = st.selectbox("Filtrer par Département :", ["France Entière"] + departements)

    st.divider()
    critere = st.selectbox("Critère à visualiser :", colonnes_analyse)


# 4. FILTRAGE

df_actif = df.copy()
if dep_choisi != "France Entière":
    df_actif = df_actif[df_actif["Département"] == dep_choisi]


# 5. TABS

tab1, tab2, tab3 = st.tabs([
    "Qualité & Métriques",
    "Distributions",
    "Top 10"
])


# ONGLET 1 — QUALITÉ DES DONNÉES

with tab1:
    st.subheader("Audit des valeurs manquantes et descriptives")

    col1, col2, col3 = st.columns(3)

    nb_nulls = df_actif[colonnes_analyse].isna().sum().sum()
    pct_nulls = (nb_nulls / (len(df_actif) * len(colonnes_analyse))) * 100

    col1.metric("Total NaN", nb_nulls)
    col2.metric("% NaN", f"{pct_nulls:.2f} %")

    anomalies_sup = len(df_actif[df_actif["superficie_km2"] <= 0])
    col3.metric("Superficie <= 0", anomalies_sup)

    st.divider()
    st.dataframe(df_actif[colonnes_analyse].describe().T, use_container_width=True)


# ONGLET 2 — DISTRIBUTIONS

with tab2:
    st.subheader(f"Visualisation intelligente : {critere}")

    c_opt1, c_opt2, c_opt3 = st.columns(3)

    with c_opt1:
        mode_echelle = st.radio(
            "Échelle",
            ["Linéaire (Standard)", "Logarithmique (Zoom étalé)"]
        )

    with c_opt2:
        filtre_taille = st.slider(
            "Cap population max",
            min_value=1000,
            max_value=int(df["population"].max()),
            value=int(df["population"].max()),
            step=5000
        )

    with c_opt3:
        afficher_box_outliers = st.checkbox("Afficher outliers", value=True)

    df_visu = df_actif[df_actif["population"] <= filtre_taille].copy()

    if mode_echelle == "Logarithmique (Zoom étalé)":
        df_visu = df_visu[df_visu[critere] > 0].copy()
        df_visu["log_" + critere] = np.log10(df_visu[critere])

    g1, g2 = st.columns(2)

    
    # HISTOGRAMME
    
    with g1:
        if mode_echelle == "Logarithmique (Zoom étalé)":
            fig_hist = px.histogram(
                df_visu,
                x="log_" + critere,
                nbins=60,
                title=f"{critere} (log)",
                color_discrete_sequence=[BLUE],
                template="plotly_white"
            )
            fig_hist.update_xaxes(title="Log10 scale")
        else:
            fig_hist = px.histogram(
                df_visu,
                x=critere,
                nbins=100,
                title=f"{critere}",
                color_discrete_sequence=[BLUE],
                template="plotly_white"
            )

        fig_hist.update_traces(marker_line_color=GRAY)
        st.plotly_chart(fig_hist, use_container_width=True)

    
    # BOXPLOT
    
    with g2:
        fig_box = px.box(
            df_visu,
            y=critere,
            title=f"Dispersion {critere}",
            color_discrete_sequence=[GRAY],
            points="all" if afficher_box_outliers else "outliers",
            log_y=(mode_echelle == "Logarithmique (Zoom étalé)"),
            template="plotly_white"
        )

        if not afficher_box_outliers:
            fig_box.update_traces(points=False)

        fig_box.update_traces(marker_line_color=GRAY)

        st.plotly_chart(fig_box, use_container_width=True)


# ONGLET 3 — EXTREMES

with tab3:
    st.subheader("Classements extrêmes")

    c3, c4 = st.columns(2)

    with c3:
        st.markdown("Top 10 population")
        st.dataframe(
            df_actif.nlargest(10, "population")[
                ["code_insee_2024", "nom_commune_2024", "population"]
            ],
            hide_index=True
        )

    with c4:
        st.markdown("Top 10 densité")
        st.dataframe(
            df_actif.nlargest(10, "densite")[
                ["code_insee_2024", "nom_commune_2024", "densite"]
            ],
            hide_index=True
        )