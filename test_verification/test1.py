import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="MSPR - Dashboard Niveaux d'études", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1f77b4; box-shadow: 1px 1px 5px rgba(0,0,0,0.05);}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CHARGEMENT DES DONNÉES
# ==========================================
@st.cache_data
def load_data():
    try:
        # On lit les fichiers générés par le script 01
        df_22 = pd.read_csv("data_filtered/2022/CLEAN_1_Niveaux_etudes_2022.csv", sep=";")
        df_hist = pd.read_csv("data_filtered/2017/CLEAN_1_Niveaux_etudes_2017.csv", sep=";")
        return df_22, df_hist
    except FileNotFoundError:
        return None, None

df_2022, df_historique = load_data()

if df_2022 is None or df_historique is None:
    st.error("❌ Fichiers de données introuvables.")
    st.warning("Assure-toi d'avoir exécuté `python scripts_v2\\01_clean_niveaux_etudes.py` avant d'ouvrir le dashboard.")
    st.stop()

# ==========================================
# 3. BARRE LATÉRALE (FILTRES GLOBAUX)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135810.png", width=80)
    st.header("Filtres")
    
    # On liste toutes les villes proprement
    toutes_villes = sorted(set(df_2022['localisation']).union(set(df_historique['localisation'])))
    ville_choisie = st.selectbox("Sélectionner une commune :", ["Toute la région"] + list(toutes_villes))
    
    st.divider()
    st.caption("Projet MSPR - Dossier 1")

# ==========================================
# 4. SÉLECTEUR D'ANNÉE (BOUTONS)
# ==========================================
st.title("Analyse des Niveaux d'Études")

choix_annee = st.radio(
    " **Choisissez l'année à analyser :**",
    ["Voir l'Historique (2017 / 2016)", "Ouvrir l'Année Cible (2022)"],
    horizontal=True
)

st.divider()

# ==========================================
# 5. APPLICATION DES FILTRES
# ==========================================
# Sélection de l'année
if "2022" in choix_annee:
    df_actif = df_2022.copy()
    annee_titre = "2022"
else:
    df_actif = df_historique.copy()
    annee_titre = "Historique (2017/2016)"

# Sélection de la ville
if ville_choisie != "Toute la région":
    df_actif = df_actif[df_actif['localisation'] == ville_choisie]

# ==========================================
# 6. AFFICHAGE DES RÉSULTATS
# ==========================================
st.markdown(f"### Données affichées : {ville_choisie} | Année : {annee_titre}")

if df_actif.empty:
    st.warning("⚠️ Aucune donnée ne correspond à tes filtres.")
else:
    # --- KPIs Globaux ---
    col1, col2, col3 = st.columns(3)
    
    # On cherche le vrai total (soit la ligne 'T', soit la somme si on a déjà enlevé 'T')
    total_recense = df_actif[df_actif['sexe'] == 'T']['nb_pers'].sum()
    if total_recense == 0: 
        total_recense = df_actif['nb_pers'].sum()
        
    diplome_top = df_actif.groupby('diplome')['nb_pers'].sum().idxmax()
    
    col1.metric("Personnes Recensées", f"{total_recense:,}".replace(",", " "))
    col2.metric("Diplôme Majoritaire", diplome_top)
    col3.metric("Lignes de données", f"{len(df_actif):,}".replace(",", " "))

    st.write("")

    # --- CRÉATION DES ONGLETS ---
    tab1, tab2, tab3 = st.tabs(["Vue Globale", "Analyse Hommes / Femmes", "Données Brutes"])

    # ---------------------------------------------------------
    # ONGLET 1 : VUE GLOBALE
    # ---------------------------------------------------------
    with tab1:
        st.markdown("**Top 10 des diplômes (Tous sexes confondus)**")
        df_bar = df_actif.groupby('diplome', as_index=False)['nb_pers'].sum().nlargest(10, 'nb_pers').sort_values('nb_pers', ascending=True)
        
        fig_bar = px.bar(
            df_bar, x='nb_pers', y='diplome', orientation='h', 
            text='nb_pers', color='nb_pers', color_continuous_scale='Blues'
        )
        fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_bar.update_layout(xaxis_title="Nombre de personnes", yaxis_title="", showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------------------------------------------------
    # ONGLET 2 : ANALYSE HOMMES / FEMMES (TES 2 TABLEAUX)
    # ---------------------------------------------------------
    with tab2:
        st.subheader("Parité : Tableaux récapitulatifs")
        
        # On isole uniquement les Hommes et les Femmes
        df_genre = df_actif[df_actif['sexe'].isin(['M', 'F'])]
        
        if df_genre.empty:
            st.info("Aucune donnée Homme/Femme disponible pour cette sélection.")
        else:
            col_tab1, col_tab2 = st.columns([1, 2])
            
            # --- TABLEAU 1 : TOTAL GLOBAL ---
            with col_tab1:
                st.markdown("##### Total Global")
                df_total = df_genre.groupby('sexe', as_index=False)['nb_pers'].sum()
                df_total['sexe'] = df_total['sexe'].map({'M': 'Hommes', 'F': 'Femmes'})
                df_total = df_total.rename(columns={'sexe': 'Genre', 'nb_pers': 'Total'})
                
                # Ajout de la ligne TOTAL
                total_somme = df_total['Total'].sum()
                df_total.loc[len(df_total)] = ['TOTAL', total_somme]
                
                st.dataframe(df_total, use_container_width=True, hide_index=True)

            # --- TABLEAU 2 : DÉTAIL PAR DIPLÔME ---
            with col_tab2:
                st.markdown("##### Détail par diplôme")
                # Tableau croisé dynamique
                pivot_genre = df_genre.pivot_table(index='diplome', columns='sexe', values='nb_pers', aggfunc='sum').fillna(0).astype(int)
                if 'M' in pivot_genre.columns: pivot_genre.rename(columns={'M': 'Hommes'}, inplace=True)
                if 'F' in pivot_genre.columns: pivot_genre.rename(columns={'F': 'Femmes'}, inplace=True)
                
                if 'Hommes' in pivot_genre.columns and 'Femmes' in pivot_genre.columns:
                    pivot_genre['Total'] = pivot_genre['Hommes'] + pivot_genre['Femmes']
                    pivot_genre = pivot_genre.sort_values('Total', ascending=False)
                
                st.dataframe(pivot_genre, use_container_width=True)

            st.divider()
            
            # --- GRAPHIQUE EN SEGMENTS ---
            st.markdown("##### Visualisation par segment (Proportion Hommes / Femmes)")
            df_genre_grouped = df_genre.groupby(['diplome', 'sexe'], as_index=False)['nb_pers'].sum()
            
            # On trie pour avoir les plus grands en haut
            diplomes_tries = pivot_genre.index.tolist()
            df_genre_grouped['diplome'] = pd.Categorical(df_genre_grouped['diplome'], categories=diplomes_tries, ordered=True)
            df_genre_grouped = df_genre_grouped.sort_values('diplome', ascending=False)

            fig_segment = px.bar(
                df_genre_grouped, 
                y='diplome', 
                x='nb_pers', 
                color='sexe', 
                orientation='h',
                barmode='stack', # Graphique empilé
                color_discrete_map={'M': "#4881d1", 'F': "#2eaf30"}, # Bleu (Hommes), Rose (Femmes)
                text='nb_pers'
            )
            fig_segment.for_each_trace(lambda t: t.update(name = 'Hommes' if t.name == 'M' else 'Femmes'))
            fig_segment.update_traces(texttemplate='%{text:.2s}', textposition='inside')
            fig_segment.update_layout(xaxis_title="Nombre de diplômés", yaxis_title="", legend_title="Genre")
            
            st.plotly_chart(fig_segment, use_container_width=True)

    # ---------------------------------------------------------
    # ONGLET 3 : EXPLORATEUR DE DONNÉES
    # ---------------------------------------------------------
    with tab3:
        st.subheader("Base de données")
        st.dataframe(df_actif, use_container_width=True, hide_index=True)
        
        csv = df_actif.to_csv(index=False, sep=";").encode('utf-8-sig')
        st.download_button(
            label=f"Télécharger les données ({annee_titre})",
            data=csv,
            file_name=f'export_{annee_titre[:4]}_{ville_choisie.replace(" ", "_")}.csv',
            mime='text/csv',
        )