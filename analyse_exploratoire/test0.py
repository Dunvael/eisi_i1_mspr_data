import streamlit as st
import pandas as pd

# 1. CONFIGURATION PAGE
st.set_page_config(
    page_title="MSPR - Référentiel Communes 2022",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Référentiel des communes - 2022")
st.markdown("Dashboard de vérification du fichier `communes_2022_cleaned.csv`.")

# 2. CHARGEMENT DES DONNÉES

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "data_cleaned/communes_2022_cleaned.csv",
            sep=";",
            dtype=str
        )

        for col in ["code_insee", "nom_commune", "code_departement", "code_region"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        return df

    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("❌ Fichier introuvable.")
    st.warning("Lance d'abord : `py scripts_v2/00_create_referentiel.py`")
    st.stop()

# 3. SIDEBAR - FILTRES
with st.sidebar:
    st.header("Filtres")

    recherche = st.text_input("Rechercher une commune :")

    departements = sorted(df["code_departement"].dropna().unique().tolist())
    dep_choisi = st.selectbox(
        "Département :",
        ["Tous"] + departements
    )

    regions = sorted(df["code_region"].dropna().unique().tolist())
    reg_choisie = st.selectbox(
        "Région :",
        ["Toutes"] + regions
    )

    st.divider()
    st.caption("Projet MSPR - Référentiel INSEE 2022")

# 4. APPLICATION DES FILTRES
df_actif = df.copy()

if recherche:
    df_actif = df_actif[
        df_actif["nom_commune"].str.contains(recherche, case=False, na=False)
    ]

if dep_choisi != "Tous":
    df_actif = df_actif[df_actif["code_departement"] == dep_choisi]

if reg_choisie != "Toutes":
    df_actif = df_actif[df_actif["code_region"] == reg_choisie]

# 5. INDICATEURS
col1, col2, col3 = st.columns(3)

col1.metric("Communes affichées", f"{len(df_actif):,}".replace(",", " "))
col2.metric("Départements", df["code_departement"].nunique())
col3.metric("Régions", df["code_region"].nunique())

st.divider()

# 6. TABLEAU
st.subheader("Données du référentiel")

if df_actif.empty:
    st.warning("⚠️ Aucune commune ne correspond aux filtres.")
else:
    st.dataframe(df_actif, use_container_width=True, hide_index=True)

    csv = df_actif.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        label="Télécharger le référentiel filtré",
        data=csv,
        file_name="export_communes_2022_cleaned.csv",
        mime="text/csv"
    )