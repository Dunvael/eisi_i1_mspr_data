import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MSPR - Taux immigration 2022",
    page_icon="🌍",
    layout="wide"
)

st.title("Analyse du taux d'immigration - 2022")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "data_cleaned/2022/06_taux_immigration_2022_cleaned.csv",
            sep=";"
        )

        df["localisation"] = df["localisation"].astype(str)
        df["taux_immigration"] = pd.to_numeric(df["taux_immigration"], errors="coerce")
        df["annee"] = df["annee"].astype(str)

        return df

    except FileNotFoundError:
        return None


df = load_data()

if df is None:
    st.error("❌ Fichier introuvable.")
    st.warning("Lance d'abord : `py cleaning_scripts/06_Taux_immigration.py`")
    st.stop()

with st.sidebar:
    st.header("Filtres")

    villes = sorted(df["localisation"].dropna().unique())
    ville = st.selectbox(
        "Choisir une commune :",
        ["Toute la France"] + villes
    )

df_actif = df.copy()

if ville != "Toute la France":
    df_actif = df_actif[df_actif["localisation"] == ville]

df_actif = df_actif.dropna(subset=["taux_immigration"])

if df_actif.empty:
    st.warning("Aucune donnée disponible.")
    st.stop()

st.subheader(f"Données : {ville}")

col1, col2, col3 = st.columns(3)

col1.metric("Taux moyen", f"{df_actif['taux_immigration'].mean():.2f} %")
col2.metric("Minimum", f"{df_actif['taux_immigration'].min():.2f} %")
col3.metric("Maximum", f"{df_actif['taux_immigration'].max():.2f} %")

st.divider()

tab1, tab2, tab3 = st.tabs(["Top communes", "Distribution", "Données"])

with tab1:
    st.subheader("Top 10 taux d'immigration élevé")

    top10 = (
        df_actif.sort_values("taux_immigration", ascending=False)
        .head(10)
        .sort_values("taux_immigration", ascending=True)
    )

    fig1 = px.bar(
        top10,
        x="taux_immigration",
        y="localisation",
        orientation="h",
        text="taux_immigration",
        color="taux_immigration",
        color_continuous_scale="Reds"
    )

    fig1.update_layout(
        xaxis_title="Taux d'immigration (%)",
        yaxis_title="",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Top 10 taux d'immigration faible")

    low10 = (
        df_actif.sort_values("taux_immigration", ascending=True)
        .head(10)
        .sort_values("taux_immigration", ascending=False)
    )

    fig2 = px.bar(
        low10,
        x="taux_immigration",
        y="localisation",
        orientation="h",
        text="taux_immigration",
        color="taux_immigration",
        color_continuous_scale="Blues"
    )

    fig2.update_layout(
        xaxis_title="Taux d'immigration (%)",
        yaxis_title="",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Distribution du taux d'immigration")

    fig_hist = px.histogram(
        df_actif,
        x="taux_immigration",
        nbins=30
    )

    fig_hist.update_layout(
        xaxis_title="Taux d'immigration (%)",
        yaxis_title="Nombre de communes"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

with tab3:
    st.subheader("Données brutes")

    st.dataframe(df_actif, use_container_width=True, hide_index=True)

    csv = df_actif.to_csv(index=False, sep=";").encode("utf-8-sig")

    st.download_button(
        label="Télécharger les données filtrées",
        data=csv,
        file_name="export_taux_immigration_2022.csv",
        mime="text/csv"
    )