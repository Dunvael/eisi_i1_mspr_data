import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os


# CONFIGURATION 

st.set_page_config(page_title="Qualité Revenus 2024", layout="wide")
st.title(" Revenus Estimés 2024")


# CHARGEMENT DATA

@st.cache_data
def load_data():
    file_path = "data_cleaned/2024/04_Revenus/04_revenus_2024_estim_clean.csv"
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path, sep=";")

df = load_data()

if df is None:
    st.error(" Fichier revenus introuvable")
    st.stop()


# COLONNE REVENUS

col_rev = "revenu_estime_2024"

if col_rev not in df.columns:
    st.error(" Colonne revenu_estime_2024 absente")
    st.stop()


# ANALYSE QUALITÉ DATA

tab1, tab2 = st.tabs([
    " Qualité des données",
    "Statistiques des revenus"
])


# TAB 1 : QUALITÉ (NA + complétude)

with tab1:
    st.subheader("Analyse des valeurs manquantes")

    total = len(df)
    na_count = df[col_rev].isna().sum()
    na_pct = round((na_count / total) * 100, 2)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Valeurs manquantes", na_count)
        st.metric("Taux de NaN (%)", na_pct)

    with col2:
        st.markdown("### Répartition NaN / OK")

        fig, ax = plt.subplots()
        ax.bar(["Valides", "Manquantes"], [total - na_count, na_count])
        ax.set_title("Qualité des données revenus")
        st.pyplot(fig)


# TAB 2 : ANALYSE STATISTIQUE DES REVENUS

with tab2:
    st.subheader("Synthèse des revenus estimés")

    st.write("### Indicateurs clés")

    st.metric("Médiane", round(df[col_rev].median(), 2))
    st.metric("Moyenne", round(df[col_rev].mean(), 2))
    st.metric("Min", round(df[col_rev].min(), 2))
    st.metric("Max", round(df[col_rev].max(), 2))

    st.divider()

    st.write("### Top / Bottom communes")

    col_nom = "nom_commune_2024" if "nom_commune_2024" in df.columns else df.columns[0]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔻 10 revenus les plus faibles")
        st.dataframe(df.nsmallest(10, col_rev)[[col_nom, col_rev]])

    with col2:
        st.markdown("#### 🔺 10 revenus les plus élevés")
        st.dataframe(df.nlargest(10, col_rev)[[col_nom, col_rev]])