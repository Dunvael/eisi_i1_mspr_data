import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Data Analytics Élections 2022",
    page_icon="",
    layout="wide"
)

# --- CHARGEMENT ET NETTOYAGE DES DONNÉES ---
@st.cache_data
def load_and_segment_data():
    # Chemin vers ton fichier généré par le script de nettoyage
    file_path = Path("data_filtered/2022/CLEAN_8_Abstention_2022.csv")
    if not file_path.exists():
        st.error(f"Fichier introuvable à l'adresse : {file_path}")
        return pd.DataFrame(), pd.DataFrame()
    
    # Lecture (Séparateur ; et décimale .)
    df = pd.read_csv(file_path, sep=";", decimal=".")
    
    # Liste étendue de mots-clés pour sortir l'étranger des stats "France"
    mots_etranger = [
        'CONSULAT', 'AMBASSADE', 'SECTION', 'ETRANGER', 'KABOUL', 'SANAA', 
        'DAMAS', 'SHANGHAI', 'KIEV', 'HAÏFA', 'TRIPOLI', 'TEHERAN', 'JERUSALEM'
    ]
    
    # Fonction de filtrage intelligente
    def filtrer_zone(nom):
        nom_up = str(nom).upper()
        if any(m in nom_up for m in mots_etranger):
            return 'Étranger'
        return '🇫🇷 France'

    df['Zone'] = df['localisation'].apply(filtrer_zone)
    
    # Séparation en deux DataFrames
    df_france = df[df['Zone'] == '🇫🇷 France'].copy()
    df_etranger = df[df['Zone'] == 'Étranger'].copy()
    
    return df_france, df_etranger

df_fr, df_et = load_and_segment_data()

# --- BARRE LATÉRALE (FILTRES) ---
st.sidebar.title("Options d'affichage")
df_complet = pd.concat([df_fr, df_et])
liste_toutes_villes = sorted(df_complet['localisation'].unique())

selection_villes = st.sidebar.multiselect(
    "Comparer des communes spécifiques :",
    options=liste_toutes_villes,
    placeholder="Ex: PARIS, MARSEILLE..."
)

# Application du filtre pour les KPIs
if selection_villes:
    df_kpi = df_complet[df_complet['localisation'].isin(selection_villes)]
else:
    df_kpi = df_complet

# --- HEADER ---
st.title("Analyse de la Participation Électorale (1er Tour 2022)")
st.markdown("---")

# --- SECTION 1 : INDICATEURS CLÉS (KPIs) ---
col1, col2, col3, col4 = st.columns(4)

t_ins = df_kpi['inscrits'].sum()
t_vot = df_kpi['votants'].sum()
t_abs = df_kpi['abstentions'].sum()
taux_abs_global = (t_abs / t_ins * 100) if t_ins > 0 else 0

with col1:
    st.metric("Total Inscrits", f"{t_ins:,.0f}".replace(",", " "))
with col2:
    st.metric("Total Votants", f"{t_vot:,.0f}".replace(",", " "))
with col3:
    st.metric("Total Abstentions", f"{t_abs:,.0f}".replace(",", " "))
with col4:
    st.metric("Taux d'Abstention", f"{taux_abs_global:.2f} %")

st.divider()

# --- SECTION 2 : ONGLETS ET GRAPHIQUES ---
tab_france, tab_etranger = st.tabs(["🇫🇷 France (Communes & DOM)", "🌍 Français de l'étranger (Consulats)"])

with tab_france:
    g1, g2 = st.columns([6, 4])
    
    with g1:
        st.subheader("Répartition Votants / Abstention")
        # 
        fig_pie_fr = px.pie(
            values=[df_fr['votants'].sum(), df_fr['abstentions'].sum()], 
            names=['Votants', 'Abstention'],
            hole=0.5,
            color_discrete_sequence=['#003366', '#BDC3C7']
        )
        st.plotly_chart(fig_pie_fr, width="stretch")
        
    with g2:
        st.subheader("Top 10 Abstention (France)")
        # 
        top_10_fr = df_fr.nlargest(10, 'taux_abstention')
        fig_bar_fr = px.bar(
            top_10_fr, x='taux_abstention', y='localisation',
            orientation='h', color='taux_abstention', 
            color_continuous_scale='Blues'
        )
        fig_bar_fr.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_bar_fr, width="stretch")

with tab_etranger:
    g3, g4 = st.columns([6, 4])
    
    with g3:
        st.subheader("Distribution de l'abstention (Monde)")
        # 
        fig_hist_et = px.histogram(
            df_et, x="taux_abstention", nbins=30,
            color_discrete_sequence=['#E63946'],
            labels={'taux_abstention': 'Taux (%)'}
        )
        st.plotly_chart(fig_hist_et, width="stretch")
        
    with g4:
        st.subheader("Top 10 Abstention (International)")
        top_10_et = df_et.nlargest(10, 'taux_abstention')
        fig_bar_et = px.bar(
            top_10_et, x='taux_abstention', y='localisation',
            orientation='h', color='taux_abstention', 
            color_continuous_scale='Reds'
        )
        fig_bar_et.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_bar_et, width="stretch")

# --- SECTION 3 : CORRÉLATION ---
st.divider()
st.subheader("Analyse de Corrélation : Taille de ville vs Abstention")
# 
fig_scatter = px.scatter(
    df_complet, x="inscrits", y="taux_abstention",
    color="Zone", size="inscrits", log_x=True,
    hover_name="localisation", opacity=0.6,
    color_discrete_map={'🇫🇷 France': '#003366', 'Étranger': '#E63946'}
)
st.plotly_chart(fig_scatter, width="stretch")

# --- SECTION 4 : TABLEAU DE DONNÉES ---
st.divider()
with st.expander("Voir les données complètes et exporter"):
    st.dataframe(
        df_kpi.style.format({"taux_abstention": "{:.2f}%", "inscrits": "{:.0f}"}),
        width="stretch"
    )
    # Bouton de téléchargement
    csv = df_kpi.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger les données en CSV", data=csv, file_name="export_election_2022.csv")