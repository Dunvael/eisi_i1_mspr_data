import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="MSPR - Dashboard Criminalité", 
    page_icon="", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS Pro : Bordure rouge foncé
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #d62728; box-shadow: 1px 1px 5px rgba(0,0,0,0.05);}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CHARGEMENT DES DONNÉES
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_filtered/2022/CLEAN_3_Criminalite_2016_2024.csv", sep=";")
        
        # On force l'année ET la localisation en texte pour le tri
        df['annee'] = df['annee'].astype(str)
        df['localisation'] = df['localisation'].astype(str)
        
        return df
    except FileNotFoundError:
        return None

df_global = load_data()

if df_global is None:
    st.error("❌ Fichier de données introuvable. Lance le script 03 de nettoyage en premier.")
    st.stop()

# ==========================================
# 3. BARRE LATÉRALE (FILTRES)
# ==========================================
with st.sidebar:
    
    st.header("Filtres d'Analyse")
    
    # Filtre Année
    liste_annees = sorted(df_global['annee'].dropna().unique(), reverse=True)
    annee_choisie = st.selectbox("Sélectionner une Année :", ["Toutes les années"] + list(liste_annees))
    
    # Filtre Commune
    liste_villes = sorted(df_global['localisation'].dropna().unique())
    ville_choisie = st.selectbox("Sélectionner une Commune :", ["Toutes les communes"] + list(liste_villes))
    
    # Filtre Type de Délit
    liste_delits = sorted(df_global['indicateur'].dropna().unique())
    delit_choisi = st.selectbox("Type d'infraction :", ["Tous les délits"] + list(liste_delits))
    
    st.divider()
    st.caption("Projet MSPR - Dossier 3 (Sécurité)")

# ==========================================
# 4. APPLICATION DES FILTRES
# ==========================================
df_filtre = df_global.copy()

if annee_choisie != "Toutes les années":
    df_filtre = df_filtre[df_filtre['annee'] == annee_choisie]
    
if ville_choisie != "Toutes les communes":
    df_filtre = df_filtre[df_filtre['localisation'] == ville_choisie]
    
if delit_choisi != "Tous les délits":
    df_filtre = df_filtre[df_filtre['indicateur'] == delit_choisi]

# ==========================================
# 5. EN-TÊTE ET KPIs
# ==========================================
st.title("Analyse de la Délinquance et Criminalité")
st.markdown(f"**Périmètre :** {ville_choisie} | **Année :** {annee_choisie} | **Délit :** {delit_choisi}")

if df_filtre.empty:
    st.warning("⚠️ Aucune donnée ne correspond à cette sélection. Les faits peuvent être classés 'non diffusables' (confidentialité).")
else:
    # --- Calculs des KPIs ---
    total_faits = df_filtre['nb_faits'].sum()
    
    # On trouve le délit le plus fréquent
    if delit_choisi == "Tous les délits":
        top_delit = df_filtre.groupby('indicateur')['nb_faits'].sum().idxmax()
    else:
        top_delit = delit_choisi
        
    # Nombre de communes impactées
    nb_communes_impactees = df_filtre[df_filtre['nb_faits'] > 0]['localisation'].nunique()

    # Affichage des KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total des Faits Enregistrés", f"{int(total_faits):,}".replace(",", " "))
    col2.metric("Infraction Majoritaire", top_delit)
    col3.metric("Communes concernées", f"{nb_communes_impactees:,}".replace(",", " "))

    st.write("")

    # ==========================================
    # 6. ONGLETS D'ANALYSE
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["Palmarès (Top 10)", "Évolution Temporelle", "Explorer la Data"])

    # ---------------------------------------------------------
    # ONGLET 1 : TOP INFRACTIONS ET COMMUNES
    # ---------------------------------------------------------
    with tab1:
        col_gauche, col_droite = st.columns(2)
        
        with col_gauche:
            st.markdown("**Top 10 des types d'infractions**")
            df_top_delits = df_filtre.groupby('indicateur', as_index=False)['nb_faits'].sum().nlargest(10, 'nb_faits').sort_values('nb_faits', ascending=True)
            
            fig_delits = px.bar(
                df_top_delits, x='nb_faits', y='indicateur', orientation='h',
                text='nb_faits', color='nb_faits', color_continuous_scale='Reds'
            )
            fig_delits.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig_delits.update_layout(xaxis_title="Nombre de faits", yaxis_title="", showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_delits, use_container_width=True)

        with col_droite:
            st.markdown("**Top 10 des communes les plus touchées**")
            df_top_villes = df_filtre.groupby('localisation', as_index=False)['nb_faits'].sum().nlargest(10, 'nb_faits').sort_values('nb_faits', ascending=True)
            
            fig_villes = px.bar(
                df_top_villes, x='nb_faits', y='localisation', orientation='h',
                text='nb_faits', color='nb_faits', color_continuous_scale='Reds'
            )
            fig_villes.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig_villes.update_layout(xaxis_title="Nombre de faits", yaxis_title="", showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_villes, use_container_width=True)

    # ---------------------------------------------------------
    # ONGLET 2 : ÉVOLUTION TEMPORELLE
    # ---------------------------------------------------------
    with tab2:
        st.subheader("Évolution des faits sur plusieurs années")
        
        if annee_choisie != "Toutes les années":
            st.info("Sélectionnez 'Toutes les années' dans le filtre de gauche pour voir une courbe d'évolution complète.")
            
        df_evolution = df_filtre.groupby('annee', as_index=False)['nb_faits'].sum().sort_values('annee')
        
        fig_line = px.line(
            df_evolution, x='annee', y='nb_faits', markers=True, 
            line_shape='spline', # Courbe lissée
            color_discrete_sequence=['#d62728'] # Ligne rouge
        )
        fig_line.update_traces(text=df_evolution['nb_faits'], textposition="top center", mode='lines+markers+text')
        fig_line.update_layout(xaxis_title="Année", yaxis_title="Total des faits enregistrés")
        
        st.plotly_chart(fig_line, use_container_width=True)

    # ---------------------------------------------------------
    # ONGLET 3 : DONNÉES BRUTES ET EXPORT
    # ---------------------------------------------------------
    with tab3:
        st.subheader("Base de données filtrée")
        st.dataframe(df_filtre, use_container_width=True, hide_index=True)
        
        # Export propre
        csv = df_filtre.to_csv(index=False, sep=";", decimal=",").encode('utf-8-sig')
        nom_ville = ville_choisie.replace(" ", "_").replace("'", "")
        nom_export = f'export_criminalite_{nom_ville}.csv' if ville_choisie != "Toutes les communes" else 'export_criminalite_global.csv'
        
        st.download_button(
            label="Télécharger l'export (Format Français)",
            data=csv,
            file_name=nom_export,
            mime='text/csv',
        )