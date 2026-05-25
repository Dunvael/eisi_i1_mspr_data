import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import missingno as msno
import os


# CONFIGURATION 

st.set_page_config(page_title="Qualité des données", layout="wide")
st.title("🩺 Audit Qualité des Données (valeurs nulles)")


# CHARGEMENT DES DONNÉES

@st.cache_data
def load_data():
    file_path = "data_cleaned/2024/03_Demographie/03_tranches_age_2024_clean.csv"
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path, sep=";")

df = load_data()

if df is None:
    st.error("Fichier introuvable")
    st.stop()


# COLONNES À ANALYSER

default_cols = ["pct_jeunes", "pct_seniors", "age_median"]
cols = [c for c in default_cols if c in df.columns]

if len(cols) == 0:
    st.error("Aucune colonne numérique trouvée pour l'analyse")
    st.stop()


# DASHBOARD QUALITÉ DATA

tab1, tab2 = st.tabs([
    " Vue globale des NaN",
    " Synthèse des valeurs manquantes"
])


# TAB 1 : VISUALISATION DES NULLS

with tab1:
    st.subheader(" Structure des valeurs manquantes")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Matrice de complétude")
        fig, ax = plt.subplots(figsize=(10, 5))
        msno.matrix(df[cols], ax=ax, sparkline=False)
        st.pyplot(fig)

    with col2:
        st.markdown("### Répartition des valeurs présentes / manquantes")
        fig, ax = plt.subplots(figsize=(6, 5))
        msno.bar(df[cols], ax=ax, color=(0.3, 0.3, 0.3))
        st.pyplot(fig)


# TAB 2 : STATS NULLS

with tab2:
    st.subheader(" Statistiques des valeurs manquantes")

    missing_abs = df[cols].isna().sum()
    missing_pct = (missing_abs / len(df) * 100).round(2)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Nombre de valeurs nulles")
        st.dataframe(missing_abs.rename("NaN count"))

    with col2:
        st.markdown("### Pourcentage de valeurs nulles")
        st.dataframe(missing_pct.rename("% NaN"))

    # graphique simple utile (UNIQUEMENT qualité data)
    st.markdown("###  Taux de valeurs manquantes par variable")

    fig, ax = plt.subplots(figsize=(6, 4))
    missing_pct.plot(kind="bar", ax=ax)
    ax.set_ylabel("% de valeurs manquantes")
    ax.set_xlabel("Variables")
    ax.set_title("Taux de NaN par colonne")
    st.pyplot(fig)