import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CONFIGURATION PAGE
# ==========================================
st.set_page_config(
    page_title="MSPR - Taux de chômage 2022",
    page_icon="📉",
    layout="wide"
)

st.title("Analyse du taux de chômage - 2022")

# ==========================================
# 2. CHARGEMENT DES DONNÉES
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "data_cleaned/2022/02_taux_chomage_2022_cleaned.csv",
            sep=";"
        )

        df["localisation"] = df["localisation"].astype(str)
        df["taux_chomage"] = pd.to_numeric(df["taux_chomage"], errors="coerce")

        return df

    except FileNotFoundError:
        return None


df = load_data()

if df is None:
    st.error("❌ Fichier introuvable")
    st.warning("Lance d'abord : py cleaning_scripts/02_Taux_chomage.py")
    st.stop()

# ==========================================
# 3. FILTRES SIDEBAR
# ==========================================
with st.sidebar:
    st.header("Filtres")

    villes = sorted(df["localisation"].dropna().unique())
    ville = st.selectbox(
        "Choisir une commune",
        ["Toute la France"] + list(villes)
    )

# ==========================================
# 4. FILTRAGE
# ==========================================
df_actif = df.copy()

if ville != "Toute la France":
    df_actif = df_actif[df_actif["localisation"] == ville]

df_actif = df_actif.dropna(subset=["taux_chomage"])

# ==========================================
# 5. KPI
# ==========================================
st.subheader(f"Données : {ville}")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Taux moyen",
    f"{df_actif['taux_chomage'].mean():.2f} %"
)

col2.metric(
    "Minimum",
    f"{df_actif['taux_chomage'].min():.2f} %"
)

col3.metric(
    "Maximum",
    f"{df_actif['taux_chomage'].max():.2f} %"
)

# ==========================================
# 6. GRAPHIQUES
# ==========================================
st.divider()

tab1, tab2, tab3 = st.tabs(["Top communes", "Distribution", "Données"])

# ------------------------------------------
# TAB 1 : TOP / FLOP
# ------------------------------------------
with tab1:
    st.subheader("Top 10 chômage élevé")

    top10 = df_actif.sort_values("taux_chomage", ascending=False).head(10)

    fig1 = px.bar(
        top10,
        x="taux_chomage",
        y="localisation",
        orientation="h",
        text="taux_chomage",
        color="taux_chomage",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Top 10 chômage faible")

    low10 = df_actif.sort_values("taux_chomage", ascending=True).head(10)

    fig2 = px.bar(
        low10,
        x="taux_chomage",
        y="localisation",
        orientation="h",
        text="taux_chomage",
        color="taux_chomage",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------
# TAB 2 : DISTRIBUTION
# ------------------------------------------
with tab2:
    st.subheader("Distribution du taux de chômage")

    fig_hist = px.histogram(
        df_actif,
        x="taux_chomage",
        nbins=30
    )

    st.plotly_chart(fig_hist, use_container_width=True)

# ------------------------------------------
# TAB 3 : TABLE
# ------------------------------------------
with tab3:
    st.subheader("Données brutes")

    st.dataframe(df_actif, use_container_width=True)

    csv = df_actif.to_csv(index=False, sep=";").encode("utf-8-sig")

    st.download_button(
        "Télécharger",
        csv,
        "export_chomage.csv",
        "text/csv"
    )