import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="MSPR - Résultats élections 2022",
    page_icon="🗳️",
    layout="wide"
)

st.title("Analyse des résultats électoraux - 1er tour 2022")


# ⚠️ PAS DE CACHE pour debug
def load_data():
    path = "data_cleaned/2022/12_resultats_elections_1er_tour_2022.csv"

    # Debug important
    st.write("📂 Dossier courant :", os.getcwd())
    st.write("📄 Fichier existe :", os.path.exists(path))

    try:
        df = pd.read_csv(
            path,
            sep=";",
            encoding="utf-8"
        )

        # Nettoyage colonnes
        df.columns = df.columns.str.strip()

        # Debug colonnes
        st.write("📊 Colonnes détectées :", df.columns.tolist())
        st.write(df.head())

        # Conversion types
        df["localisation"] = df["localisation"].astype(str)
        df["classe_politique"] = df["classe_politique"].astype(str)

        cols_scores = [
            "score_extreme_droite",
            "score_extreme_gauche",
            "score_centre",
            "score_droite",
            "score_gauche",
        ]

        for col in cols_scores:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    except Exception as e:
        st.error(f"Erreur chargement : {e}")
        return None


df = load_data()

if df is None:
    st.stop()


# ========================
# FILTRES
# ========================
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

if df_actif.empty:
    st.warning("Aucune donnée disponible.")
    st.stop()


# ========================
# METRICS
# ========================
st.subheader(f"Données : {ville}")

col1, col2, col3 = st.columns(3)

classe_majoritaire = df_actif["classe_politique"].mode()[0]
nb_communes = len(df_actif)

score_moyen_gagnant = df_actif[
    [
        "score_extreme_droite",
        "score_extreme_gauche",
        "score_centre",
        "score_droite",
        "score_gauche",
    ]
].max(axis=1).mean()

col1.metric("Classe politique dominante", classe_majoritaire)
col2.metric("Nombre de communes", f"{nb_communes}")
col3.metric("Score gagnant moyen", f"{score_moyen_gagnant:.2f} %")


st.divider()


# ========================
# TABS
# ========================
tab1, tab2, tab3 = st.tabs(["Répartition politique", "Scores moyens", "Données"])


# ========================
# TAB 1
# ========================
with tab1:
    st.subheader("Répartition des communes par classe politique")

    repartition = (
        df_actif["classe_politique"]
        .value_counts()
        .reset_index()
    )

    repartition.columns = ["classe_politique", "nombre_communes"]

    fig = px.bar(
        repartition,
        x="classe_politique",
        y="nombre_communes",
        text="nombre_communes",
        color="classe_politique"
    )

    fig.update_layout(
        xaxis_title="Classe politique",
        yaxis_title="Nombre de communes",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


# ========================
# TAB 2
# ========================
with tab2:
    st.subheader("Scores moyens par bloc politique")

    cols_scores = [
        "score_extreme_droite",
        "score_extreme_gauche",
        "score_centre",
        "score_droite",
        "score_gauche",
    ]

    scores_moyens = df_actif[cols_scores].mean().reset_index()
    scores_moyens.columns = ["bloc_politique", "score_moyen"]

    fig_scores = px.bar(
        scores_moyens,
        x="bloc_politique",
        y="score_moyen",
        text="score_moyen",
        color="bloc_politique"
    )

    fig_scores.update_layout(
        xaxis_title="Bloc politique",
        yaxis_title="Score moyen (%)",
        showlegend=False
    )

    st.plotly_chart(fig_scores, use_container_width=True)


# ========================
# TAB 3
# ========================
with tab3:
    st.subheader("Données nettoyées")

    st.dataframe(df_actif, use_container_width=True, hide_index=True)

    csv = df_actif.to_csv(index=False, sep=";").encode("utf-8-sig")

    st.download_button(
        label="Télécharger",
        data=csv,
        file_name="export_resultats_elections_2022.csv",
        mime="text/csv"
    )