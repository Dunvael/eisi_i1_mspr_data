import streamlit as st
import pandas as pd
import numpy as np
import os


# CONFIGURATION 

st.set_page_config(page_title="Criminalité ", layout="wide")
st.title("Criminalité 2024")


# CHARGEMENT DES DONNÉES

@st.cache_data
def load_data():
    # Chemin du dataset de criminalité 2024
    file_path = "data_cleaned/2024/02_Criminalite/02_criminalite_diff_ndiff_2024_cleaned.csv"
    if not os.path.exists(file_path):
        return None

    return pd.read_csv(file_path, sep=";")

df = load_data()

if df is None:
    st.error("Fichier introuvable")
    st.stop()
# VARIABLES CRIMINALITÉ ANALYSÉES
crime_cols = [
    "taux_violences_intrafamiliales",
    "taux_violences_sexuelles",
    "taux_vols_avec_armes",
    "taux_vols_violents_sans_arme",
    "taux_cambriolages_logement",
    "taux_vols_vehicule",
    "taux_degradations",
    "taux_usage_stupefiants",
    "taux_trafic_stupefiants"
]


# SIDEBAR

with st.sidebar:
    search = st.text_input("🔎 Commune")

df_actif = df.copy()

if search:
    df_actif = df_actif[
        df_actif["nom_commune_2024"].str.contains(search, case=False, na=False)
    ]


# KPI GLOBAL

st.subheader("Qualité des données")
# Nombre total de cellules analysées
total_cells = len(df_actif) * len(crime_cols)
# Comptage des valeurs manquantes
missing_cells = df_actif[crime_cols].isna().sum().sum()
# Score de qualité global (1 = parfait, 0 = très mauvais)
score = 1 - (missing_cells / total_cells)

c1, c2, c3 = st.columns(3)

c1.metric("Score qualité", f"{score:.2%}")
c2.metric("Nombre de NaN", missing_cells)
c3.metric("Communes analysées", len(df_actif))

st.divider()


# NAN PAR INDICATEUR (NOMBRE)

st.subheader("Nombre de valeurs manquantes par indicateur")

nan_count = df_actif[crime_cols].isna().sum().sort_values(ascending=False)

st.bar_chart(nan_count)

st.caption("Plus la barre est haute → plus l’indicateur est incomplet")

st.divider()


# Moyenne simple des indicateurs de criminalité
df_actif["risk_score"] = df_actif[crime_cols].mean(axis=1)


# COMMUNES LES PLUS À RISQUE
st.subheader("Communes les plus à risque")

st.dataframe(
    df_actif.nlargest(10, "risk_score")[
        ["code_insee_2024", "nom_commune_2024", "risk_score"]
    ],
    hide_index=True
)

st.divider()


# DISTRIBUTION

st.subheader("Distribution d’un indicateur")

col = st.selectbox("Indicateur :", crime_cols)

c1, c2 = st.columns(2)

with c1:
    st.write("Statistiques")
    st.dataframe(df_actif[col].describe())

with c2:
    st.write("Distribution")
    st.bar_chart(df_actif[col].dropna())

st.divider()


# MOYENNES DES INDICATEURS DE CRIMINALITÉ
st.subheader("Niveau moyen des crimes")

mean_values = df_actif[crime_cols].mean().sort_values(ascending=False)

st.bar_chart(mean_values)

st.caption("Permet d’identifier les crimes les plus fréquents")

st.divider()


# NAN PAR COMMUNE

st.subheader("Communes avec données incomplètes")

df_actif["missing_count"] = df_actif[crime_cols].isna().sum(axis=1)

st.bar_chart(df_actif["missing_count"])

st.caption("Plus élevé = données manquantes par commune")

st.divider()


# TOP 10 PAR INDICATEUR CHOISI

st.subheader("Top 10 par indicateur")

col2 = st.selectbox("Choisir indicateur", crime_cols, key="top")

st.dataframe(
    df_actif.nlargest(10, col2)[
        ["code_insee_2024", "nom_commune_2024", col2]
    ],
    hide_index=True
)