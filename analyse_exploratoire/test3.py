import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CONFIG PAGE
# ==========================================
st.set_page_config(
    page_title="MSPR - categorie sociale 2022",
    page_icon="👥",
    layout="wide"
)

st.title("Analyse de la categorie sociale - 2022")

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "data_cleaned/2022/03_categorie_sociale_2022.csv",
            sep=";"
        )

        df["localisation"] = df["localisation"].astype(str)

        cols = ["pourcentage_agri", "pourcentage_cadres", "pourcentage_employes", "pourcentage_ouvriers"]
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    except FileNotFoundError:
        return None


df = load_data()

if df is None:
    st.error("❌ Fichier introuvable")
    st.warning("Lance d'abord : py cleaning_scripts/03_categorie_sociale.py")
    st.stop()

# ==========================================
# 3. FILTRES
# ==========================================
with st.sidebar:
    st.header("Filtres")

    villes = sorted(df["localisation"].dropna().unique())
    ville = st.selectbox(
        "Choisir une commune",
        ["Toute la France"] + villes
    )

# ==========================================
# 4. FILTRAGE
# ==========================================
df_actif = df.copy()

if ville != "Toute la France":
    df_actif = df_actif[df_actif["localisation"] == ville]

# ==========================================
# 5. KPI
# ==========================================
st.subheader(f"Données : {ville}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Agriculteurs", f"{df_actif['pourcentage_agri'].mean():.2f} %")
col2.metric("Cadres", f"{df_actif['pourcentage_cadres'].mean():.2f} %")
col3.metric("Employés", f"{df_actif['pourcentage_employes'].mean():.2f} %")
col4.metric("Ouvriers", f"{df_actif['pourcentage_ouvriers'].mean():.2f} %")

# ==========================================
# 6. GRAPHIQUES
# ==========================================
st.divider()

tab1, tab2, tab3 = st.tabs(["Répartition", "Comparaison communes", "Données"])

# -----------------------------
# TAB 1 : CAMEMBERT
# -----------------------------
with tab1:
    st.subheader("Répartition moyenne")

    df_pie = pd.DataFrame({
        "categorie": ["Agriculteurs", "Cadres", "Employés", "Ouvriers"],
        "valeur": [
            df_actif["pourcentage_agri"].mean(),
            df_actif["pourcentage_cadres"].mean(),
            df_actif["pourcentage_employes"].mean(),
            df_actif["pourcentage_ouvriers"].mean()
        ]
    })

    fig = px.pie(df_pie, names="categorie", values="valeur")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 2 : TOP COMMUNES
# -----------------------------
with tab2:
    st.subheader("Top communes (ouvriers)")

    top = df.sort_values("pourcentage_ouvriers", ascending=False).head(10)

    fig = px.bar(
        top,
        x="pourcentage_ouvriers",
        y="localisation",
        orientation="h",
        text="pourcentage_ouvriers",
        color="pourcentage_ouvriers",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 3 : DATA
# -----------------------------
with tab3:
    st.subheader("Données brutes")

    st.dataframe(df_actif, use_container_width=True)

    csv = df_actif.to_csv(index=False, sep=";").encode("utf-8-sig")

    st.download_button(
        "Télécharger",
        csv,
        "export_categorie_sociale.csv",
        "text/csv"
    )