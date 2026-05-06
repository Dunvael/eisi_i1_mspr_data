import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(
    page_title="MSPR - Démographie 2022",
    page_icon="👥",
    layout="wide"
)

st.title("Analyse démographique - 2022")

# ==========================================
# LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "data_cleaned/2022/05_demographie_2022.csv",
            sep=";"
        )

        df["localisation"] = df["localisation"].astype(str)

        cols = ["pct_jeunes", "pct_seniors", "age_median"]
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    except FileNotFoundError:
        return None


df = load_data()

if df is None:
    st.error("❌ Fichier introuvable.")
    st.stop()

# ==========================================
# FILTRES
# ==========================================
with st.sidebar:
    st.header("Filtres")

    villes = sorted(df["localisation"].dropna().unique())
    ville = st.selectbox("Commune :", ["Toutes"] + villes)

# ==========================================
# FILTRAGE
# ==========================================
df_actif = df.copy()

if ville != "Toutes":
    df_actif = df_actif[df_actif["localisation"] == ville]

if df_actif.empty:
    st.warning("Aucune donnée")
    st.stop()

# ==========================================
# KPIs
# ==========================================
col1, col2, col3 = st.columns(3)

col1.metric(
    "% jeunes",
    f"{df_actif['pct_jeunes'].mean():.2f}%"
)

col2.metric(
    "% seniors",
    f"{df_actif['pct_seniors'].mean():.2f}%"
)

col3.metric(
    "Âge médian",
    f"{df_actif['age_median'].mean():.1f} ans"
)

st.divider()

# ==========================================
# GRAPHIQUE 1 : Top jeunes
# ==========================================
st.subheader("Top 10 communes les plus jeunes")

df_top_jeunes = (
    df.sort_values("pct_jeunes", ascending=False)
    .head(10)
)

fig1 = px.bar(
    df_top_jeunes,
    x="pct_jeunes",
    y="localisation",
    orientation="h",
    text="pct_jeunes",
    color="pct_jeunes",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# GRAPHIQUE 2 : Top seniors
# ==========================================
st.subheader("Top 10 communes les plus âgées")

df_top_seniors = (
    df.sort_values("pct_seniors", ascending=False)
    .head(10)
)

fig2 = px.bar(
    df_top_seniors,
    x="pct_seniors",
    y="localisation",
    orientation="h",
    text="pct_seniors",
    color="pct_seniors",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# GRAPHIQUE 3 : âge médian
# ==========================================
st.subheader("Top 10 âge médian le plus élevé")

df_age = (
    df.sort_values("age_median", ascending=False)
    .head(10)
)

fig3 = px.bar(
    df_age,
    x="age_median",
    y="localisation",
    orientation="h",
    text="age_median",
    color="age_median",
    color_continuous_scale="Viridis"
)

st.plotly_chart(fig3, use_container_width=True)

# ==========================================
# TABLE
# ==========================================
st.subheader("Données brutes")

st.dataframe(df_actif, use_container_width=True)

# Export CSV
csv = df_actif.to_csv(index=False, sep=";").encode("utf-8-sig")

st.download_button(
    label="Télécharger",
    data=csv,
    file_name="demographie.csv",
    mime="text/csv"
)