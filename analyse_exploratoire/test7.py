import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MSPR - Associations 2022",
    page_icon="🏛️",
    layout="wide"
)

st.title("Analyse du nombre d'associations - 2022")

# ==========================================
# LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "data_cleaned/2022/07_associations_2022.csv",
            sep=";"
        )

        df["localisation"] = df["localisation"].astype(str)
        df["nb_associations"] = pd.to_numeric(df["nb_associations"], errors="coerce")

        return df

    except FileNotFoundError:
        return None


df = load_data()

if df is None:
    st.error("❌ Fichier introuvable")
    st.warning("Lance : py cleaning_scripts/07_associations.py")
    st.stop()

# ==========================================
# FILTRES
# ==========================================
with st.sidebar:
    st.header("Filtres")

    villes = sorted(df["localisation"].dropna().unique())

    ville = st.selectbox(
        "Choisir une commune",
        ["Toute la France"] + villes
    )

df_actif = df.copy()

if ville != "Toute la France":
    df_actif = df_actif[df_actif["localisation"] == ville]

df_actif = df_actif.dropna(subset=["nb_associations"])

if df_actif.empty:
    st.warning("Aucune donnée disponible")
    st.stop()

# ==========================================
# METRICS
# ==========================================
st.subheader(f"Données : {ville}")

col1, col2, col3 = st.columns(3)

col1.metric("Moyenne", f"{df_actif['nb_associations'].mean():.0f}")
col2.metric("Minimum", f"{df_actif['nb_associations'].min():.0f}")
col3.metric("Maximum", f"{df_actif['nb_associations'].max():.0f}")

st.divider()

# ==========================================
# TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["Top communes", "Distribution", "Données"])

# ---------- TOP ----------
with tab1:
    st.subheader("Top 10 communes (plus d'associations)")

    top10 = (
        df_actif.sort_values("nb_associations", ascending=False)
        .head(10)
        .sort_values("nb_associations", ascending=True)
    )

    fig1 = px.bar(
        top10,
        x="nb_associations",
        y="localisation",
        orientation="h",
        text="nb_associations",
        color="nb_associations",
        color_continuous_scale="Greens"
    )

    fig1.update_layout(
        xaxis_title="Nombre d'associations",
        yaxis_title="",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Top 10 communes (moins d'associations)")

    low10 = (
        df_actif.sort_values("nb_associations", ascending=True)
        .head(10)
        .sort_values("nb_associations", ascending=False)
    )

    fig2 = px.bar(
        low10,
        x="nb_associations",
        y="localisation",
        orientation="h",
        text="nb_associations",
        color="nb_associations",
        color_continuous_scale="Blues"
    )

    fig2.update_layout(
        xaxis_title="Nombre d'associations",
        yaxis_title="",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------- DISTRIBUTION ----------
with tab2:
    st.subheader("Distribution")

    fig_hist = px.histogram(
        df_actif,
        x="nb_associations",
        nbins=40
    )

    fig_hist.update_layout(
        xaxis_title="Nombre d'associations",
        yaxis_title="Nombre de communes"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

# ---------- DATA ----------
with tab3:
    st.subheader("Données brutes")

    st.dataframe(df_actif, use_container_width=True, hide_index=True)

    csv = df_actif.to_csv(index=False, sep=";").encode("utf-8-sig")

    st.download_button(
        label="Télécharger",
        data=csv,
        file_name="export_associations_2022.csv",
        mime="text/csv"
    )