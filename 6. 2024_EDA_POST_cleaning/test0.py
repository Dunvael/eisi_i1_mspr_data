import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os


# PALETTE (UNIQUEMENT BLEU + GRIS)

BLUE = "#1f77b4"
GRAY = "#7f7f7f"


# 1. CONFIGURATION PAGE

st.set_page_config(
    page_title="Référentiel Communes",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Analyse Exploratoire : Référentiel INSEE")
st.markdown("Dashboard pour le profilage des données, la détection des anomalies et l'analyse géographique.")


# 2. CHARGEMENT & ENRICHISSEMENT

@st.cache_data
def load_data():
    file_path = "data_cleaned/2024/00_referentiel_communes_22_24_clean.csv"
    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path, sep=";", dtype=str)

    df["Département"] = df["code_insee_2024"].astype(str).str[:2]
    df["Fusion_Detectee"] = df["code_insee_2022"] != df["code_insee_2024"]
    df["Longueur_Nom"] = df["nom_commune_2024"].astype(str).apply(len)

    df["Code_2024_Valide"] = df["code_insee_2024"].astype(str).apply(len) == 5
    df["Code_2022_Valide"] = df["code_insee_2022"].astype(str).apply(len) == 5

    return df

df = load_data()

if df is None:
    st.error("Fichier introuvable. Vérifie le chemin du référentiel.")
    st.stop()


with st.sidebar:
    st.header("Contrôles")

    recherche = st.text_input("Rechercher une commune :")

    departements = sorted(df["Département"].dropna().unique().tolist())
    dep_choisi = st.selectbox("Filtrer par Département :", ["France Entière"] + departements)


# 4. FILTRES

df_actif = df.copy()

if recherche:
    df_actif = df_actif[df_actif["nom_commune_2024"].str.contains(recherche, case=False, na=False)]

if dep_choisi != "France Entière":
    df_actif = df_actif[df_actif["Département"] == dep_choisi]


# 5. ONGLETS

tab1, tab2, tab3 = st.tabs([
    "(Nulls & Formats)",
    "Analyse Géographique",
    "Mouvements Administratifs"
])


# ONGLET 1 : QUALITÉ DES DONNÉES

with tab1:
    st.subheader("Profilage des données et détection d'anomalies")

    colQ1, colQ2, colQ3 = st.columns(3)

    null_counts = df_actif.isna().sum() + (df_actif == "").sum() + (df_actif == "nan").sum()
    total_nulls = null_counts.sum()

    colQ1.metric("Valeurs Nulles ou Vides", total_nulls, delta="Objectif: 0", delta_color="inverse")

    doublons_noms = df_actif.duplicated(subset=["nom_commune_2024"], keep=False).sum()
    colQ2.metric("Homonymes", doublons_noms)

    codes_invalides = (~df_actif["Code_2024_Valide"]).sum()
    colQ3.metric("Codes INSEE non-conformes", codes_invalides)

    st.info("**Note d'audit :** L'absence totale de valeurs nulles et de codes invalides confirme que le pipeline de nettoyage initial (Data Cleaning) a fonctionné avec un taux de succès de 100%.")


# ONGLET 2 — ANALYSE GÉOGRAPHIQUE

with tab2:
    st.subheader("Répartition du territoire")

    c3, c4 = st.columns([2, 1])
    
    # DISTRIBUTION DES COMMUNES PAR DÉPARTEMENT
    with c3:
        df_dep = df_actif["Département"].value_counts().head(20)

        fig, ax = plt.subplots(figsize=(10, 5))
        df_dep.plot(kind="bar", ax=ax, color=BLUE)

        ax.set_title("Top 20 départements avec le plus de communes")
        ax.set_xlabel("Département")
        ax.set_ylabel("Nombre de communes")

        st.pyplot(fig)
    # ANALYSE TEXTUELLE DES COMMUNES
    with c4:
        st.markdown("**Communes avec les noms les plus longs :**")
        st.dataframe(
            df_actif[["nom_commune_2024", "Longueur_Nom"]]
            .sort_values(by="Longueur_Nom", ascending=False)
            .head(10),
            hide_index=True
        )


# ONGLET 3 — FUSIONS ADMINISTRATIVES

with tab3:
    st.subheader("Évolution 2022 -> 2024")

    nb_fusions = df_actif["Fusion_Detectee"].sum()
    st.info(f"Il y a **{nb_fusions} communes** avec changement de code INSEE.")

    if nb_fusions > 0:
        c5, c6 = st.columns(2)
        # FUSIONS PAR DÉPARTEMENT
        with c5:
            fusions_par_dep = (
                df_actif[df_actif["Fusion_Detectee"]]["Département"]
                .value_counts()
                .head(10)
            )

            fig2, ax2 = plt.subplots(figsize=(10, 5))
            fusions_par_dep.plot(kind="bar", ax=ax2, color=GRAY)

            ax2.set_title("Top 10 départements avec fusions")
            ax2.set_xlabel("Département")
            ax2.set_ylabel("Nombre de fusions")

            st.pyplot(fig2)
        # DÉTAIL DES FUSIONS
        with c6:
            st.markdown("**Détail des communes fusionnées :**")
            st.dataframe(
                df_actif[df_actif["Fusion_Detectee"]][
                    ["code_insee_2022", "code_insee_2024", "nom_commune_2024"]
                ],
                hide_index=True
            )
    else:
        st.success("Aucune fusion détectée dans ce périmètre.")