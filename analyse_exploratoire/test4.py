import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CONFIG
# ==========================================
st.set_page_config(
    page_title="MSPR - Densité population 2022",
    page_icon="🏙️",
    layout="wide"
)

st.title("Analyse densité et population - 2022")

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "data_cleaned/2022/04_densite_population_2022.csv",
            sep=";"
        )

        df["localisation"] = df["localisation"].astype(str)

        df["population"] = pd.to_numeric(df["population"], errors="coerce")
        df["superficie_km2"] = pd.to_numeric(df["superficie_km2"], errors="coerce")
        df["densite"] = pd.to_numeric(df["densite"], errors="coerce")

        return df

    except FileNotFoundError:
        return None


df = load_data()

if df is None:
    st.error("❌ Fichier introuvable")
    st.warning("Lance d'abord : py cleaning_scripts/04_Densite_population.py")
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
# 5. KPIs
# ==========================================
st.subheader(f"Données : {ville}")

col1, col2, col3 = st.columns(3)

col1.metric("Population", f"{int(df_actif['population'].mean()):,}".replace(",", " "))
col2.metric("Superficie (km²)", f"{df_actif['superficie_km2'].mean():.2f}")
col3.metric("Densité (hab/km²)", f"{df_actif['densite'].mean():.2f}")

# ==========================================
# 6. GRAPHIQUES
# ==========================================
st.divider()

tab1, tab2, tab3 = st.tabs(["Top densité", "Corrélation", "Données"])

# -----------------------------
# TAB 1 : TOP DENSITÉ
# -----------------------------
with tab1:
    st.subheader("Top 10 densité")

    top = df.sort_values("densite", ascending=False).head(10)

    fig = px.bar(
        top,
        x="densite",
        y="localisation",
        orientation="h",
        text="densite",
        color="densite",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 2 : CORRÉLATION
# -----------------------------
with tab2:
    st.subheader("Population vs densité")

    fig = px.scatter(
        df,
        x="population",
        y="densite",
        hover_name="localisation",
        opacity=0.6
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 3 : TABLE
# -----------------------------
with tab3:
    st.subheader("Données brutes")

    st.dataframe(df_actif, use_container_width=True)

    csv = df_actif.to_csv(index=False, sep=";").encode("utf-8-sig")

    st.download_button(
        "Télécharger",
        csv,
        "export_densite_population.csv",
        "text/csv"
    )