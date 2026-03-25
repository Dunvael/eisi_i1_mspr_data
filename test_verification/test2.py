import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MSPR - Dashboard Densité", page_icon="🗺️", layout="wide")

st.markdown("""
    <style>.stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #2ca02c; }</style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # On lit avec la virgule !
        return pd.read_csv("data_filtered/2022/CLEAN_2_Densite_population_2022.csv", sep=";", decimal=",")
    except FileNotFoundError:
        return None

df_global = load_data()

if df_global is None:
    st.error("❌ Fichier introuvable.")
    st.stop()

# --- FILTRES ---
with st.sidebar:
    st.header("Filtres Géographiques")
    
    liste_regions = sorted(df_global['region'].dropna().unique())
    region_choisie = st.selectbox("Région :", ["Toute la France"] + list(liste_regions))
    
    df_filtre = df_global[df_global['region'] == region_choisie] if region_choisie != "Toute la France" else df_global.copy()
        
    liste_deps = sorted(df_filtre['departement'].dropna().unique())
    dep_choisi = st.selectbox("Département :", ["Tous les départements"] + list(liste_deps))
    
    if dep_choisi != "Tous les départements":
        df_filtre = df_filtre[df_filtre['departement'] == dep_choisi]

# --- EN-TÊTE ---
st.title("Analyse de la Densité de Population (2022)")

if df_filtre.empty:
    st.warning("⚠️ Aucune donnée.")
else:
    total_pop = df_filtre['nb_pers'].sum()
    total_superficie = df_filtre['superficie_km2'].sum()
    densite_moyenne = round((total_pop / total_superficie), 2) if total_superficie > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Population Totale", f"{int(total_pop):,}".replace(",", " "))
    col2.metric("Superficie (km²)", f"{int(total_superficie):,}")
    col3.metric("Densité Moyenne", f"{densite_moyenne}".replace(".", ",") + " hab/km²")
    col4.metric("Nb de Communes", f"{len(df_filtre):,}".replace(",", " "))

    st.write("")
    tab1, tab2, tab3 = st.tabs(["Palmarès (Top 10)", "Grille de Densité", "Explorer la Data"])

    with tab1:
        col_gauche, col_droite = st.columns(2)
        with col_gauche:
            st.markdown("**Top 10 des communes par Population**")
            fig_pop = px.bar(df_filtre.nlargest(10, 'nb_pers').sort_values('nb_pers'), x='nb_pers', y='localisation', orientation='h', text='nb_pers', color='nb_pers', color_continuous_scale='Blues')
            fig_pop.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig_pop.update_layout(xaxis_title="Habitants", yaxis_title="", showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_pop, use_container_width=True)

        with col_droite:
            st.markdown("**Top 10 des communes par Densité**")
            fig_dense = px.bar(df_filtre.nlargest(10, 'densite').sort_values('densite'), x='densite', y='localisation', orientation='h', color='densite', color_continuous_scale='Reds', text='densite')
            fig_dense.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_dense.update_layout(xaxis_title="Densité (hab/km²)", yaxis_title="", showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_dense, use_container_width=True)

    with tab2:
        df_grille = df_filtre['type_densite'].value_counts().reset_index()
        df_grille.columns = ['Code Grille', 'Nombre de communes']
        df_grille['Code Grille'] = df_grille['Code Grille'].astype(str)
        fig_pie = px.pie(df_grille, values='Nombre de communes', names='Code Grille', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        st.subheader("Base de données filtrée")
        df_affichage = df_filtre.copy()
        
        # On force l'affichage de la virgule à l'écran pour le jury
        df_affichage['densite'] = df_affichage['densite'].apply(lambda x: f"{float(x):.2f}".replace('.', ','))

        
        st.dataframe(df_affichage, use_container_width=True, hide_index=True)
        
        csv = df_filtre.to_csv(index=False, sep=";", decimal=",").encode('utf-8-sig')
        nom_export = f'export_densite_{region_choisie.replace(" ", "_")}.csv' if region_choisie != "Toute la France" else 'export_densite_france.csv'
        st.download_button("Télécharger cet export", data=csv, file_name=nom_export, mime='text/csv')