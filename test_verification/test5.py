import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(page_title="Dashboard INSEE - MSPR", page_icon="", layout="wide")

# ==========================================
# 2. CHARGEMENT DES DONNÉES
# ==========================================
@st.cache_data
def load_data():
    chemin_fichier = Path("data_filtered/2022/CLEAN_5_Nationalite_2022.csv")
    if chemin_fichier.exists():
        return pd.read_csv(chemin_fichier, sep=";", decimal=".")
    return None

df = load_data()

# ==========================================
# 3. INTERFACE & FILTRES DYNAMIQUES
# ==========================================
if df is None:
    st.error("⚠️ Fichier introuvable. Vérifiez le chemin dans load_data().")
else:
    # --- BARRE LATÉRALE ---
    st.sidebar.title("Filtres d'Analyse")
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### Localisation")
    vue_globale = st.sidebar.checkbox("Toutes les communes (Vue Globale)", value=False)
    
    liste_communes = df['localisation'].sort_values().unique()
    
    if vue_globale:
        df_cible = df.copy()
        titre_localisation = "Vue Globale (Toutes les communes)"
    else:
        communes_selectionnees = st.sidebar.multiselect(
            "Choisissez une ou plusieurs communes :", 
            options=liste_communes,
            default=["PARIS"] if "PARIS" in liste_communes else [liste_communes[0]]
        )
        df_cible = df[df['localisation'].isin(communes_selectionnees)].copy()
        
        if len(communes_selectionnees) == 1:
            titre_localisation = communes_selectionnees[0]
        elif len(communes_selectionnees) > 1:
            titre_localisation = f"Sélection multiple ({len(communes_selectionnees)} communes)"
        else:
            titre_localisation = "Aucune commune sélectionnée"
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Critères de population")
    
    dico_ages = {"15 à 24 ans": "_15_24", "25 à 54 ans": "_25_54", "55 ans et plus": "_55_PLUS"}
    ages_selectionnes = st.sidebar.multiselect("Âge :", options=list(dico_ages.keys()), default=list(dico_ages.keys()))
    
    dico_nat = {"Français": "FR", "Étrangers": "ET"}
    nat_selectionnees = st.sidebar.multiselect("Nationalité :", options=list(dico_nat.keys()), default=list(dico_nat.keys()))

    # ==========================================
    # 4. CALCULS BASÉS SUR LES FILTRES
    # ==========================================
    if len(ages_selectionnes) == 0 or len(nat_selectionnees) == 0 or (not vue_globale and len(communes_selectionnees) == 0):
        st.warning("⚠️ Veuillez sélectionner au moins une localisation, une tranche d'âge et une nationalité.")
    else:
        # On calcule le total filtré global ET par commune (pour le palmarès et le tableau)
        total_fr_filtre = 0
        total_et_filtre = 0
        df_cible['Total_Filtre'] = 0 # Nouvelle colonne pour stocker le total dynamique par ligne
        
        for age in ages_selectionnes:
            suffixe = dico_ages[age]
            if "Français" in nat_selectionnees:
                df_cible['Total_Filtre'] += df_cible[f"FR{suffixe}"]
                total_fr_filtre += df_cible[f"FR{suffixe}"].sum()
            if "Étrangers" in nat_selectionnees:
                df_cible['Total_Filtre'] += df_cible[f"ET{suffixe}"]
                total_et_filtre += df_cible[f"ET{suffixe}"].sum()
                
        total_global_filtre = total_fr_filtre + total_et_filtre

        # ==========================================
        # 5. AFFICHAGE DU DASHBOARD
        # ==========================================
        st.title(f"Analyse Démographique : {titre_localisation}")
        st.markdown(f"*(Données filtrées selon vos critères dans le menu latéral)*")
        
        # --- KPIs ---
        st.markdown("### Indicateurs filtrés")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Population Sélectionnée", f"{total_global_filtre:,.0f}".replace(',', ' '))
        col2.metric("Français", f"{total_fr_filtre:,.0f}".replace(',', ' '))
        col3.metric("Étrangers", f"{total_et_filtre:,.0f}".replace(',', ' '))
        pct_et = (total_et_filtre / total_global_filtre * 100) if total_global_filtre > 0 else 0
        col4.metric("Part d'étrangers", f"{pct_et:.1f} %")
        st.markdown("---")

        # --- PREMIÈRE LIGNE DE GRAPHIQUES ---
        g1_col1, g1_col2 = st.columns(2)

        with g1_col1:
            st.markdown("#### Volumes par âge et nationalité")
            valeurs_bar_fr = [df_cible[f"FR{dico_ages[age]}"].sum() if "Français" in nat_selectionnees else 0 for age in ages_selectionnes]
            valeurs_bar_et = [df_cible[f"ET{dico_ages[age]}"].sum() if "Étrangers" in nat_selectionnees else 0 for age in ages_selectionnes]

            fig_bar = go.Figure()
            if "Français" in nat_selectionnees:
                fig_bar.add_trace(go.Bar(name='Français', x=ages_selectionnes, y=valeurs_bar_fr, marker_color='#1f77b4'))
            if "Étrangers" in nat_selectionnees:
                fig_bar.add_trace(go.Bar(name='Étrangers', x=ages_selectionnes, y=valeurs_bar_et, marker_color='#ff7f0e'))
            
            fig_bar.update_layout(barmode='group', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=0))
            st.plotly_chart(fig_bar, use_container_width=True)

        with g1_col2:
            st.markdown("#### Poids des tranches d'âge")
            valeurs_pie = [
                (df_cible[f"FR{dico_ages[age]}"].sum() if "Français" in nat_selectionnees else 0) + 
                (df_cible[f"ET{dico_ages[age]}"].sum() if "Étrangers" in nat_selectionnees else 0) 
                for age in ages_selectionnes
            ]
            fig_pie = px.pie(values=valeurs_pie, names=ages_selectionnes, hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
            fig_pie.update_layout(margin=dict(t=30, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        # --- DEUXIÈME LIGNE DE GRAPHIQUES ---
        g2_col1, g2_col2 = st.columns(2)

        with g2_col1:
            st.markdown("#### Hiérarchie de la population (Treemap)")
            treemap_data = []
            for age in ages_selectionnes:
                if "Français" in nat_selectionnees:
                    val = df_cible[f"FR{dico_ages[age]}"].sum()
                    if val > 0: treemap_data.append({"Nationalité": "Français", "Âge": age, "Population": val})
                if "Étrangers" in nat_selectionnees:
                    val = df_cible[f"ET{dico_ages[age]}"].sum()
                    if val > 0: treemap_data.append({"Nationalité": "Étrangers", "Âge": age, "Population": val})
            
            if treemap_data:
                df_tree = pd.DataFrame(treemap_data)
                fig_tree = px.treemap(df_tree, path=['Nationalité', 'Âge'], values='Population', color='Nationalité')
                fig_tree.update_layout(margin=dict(t=30, b=0))
                st.plotly_chart(fig_tree, use_container_width=True)
            else:
                st.info("Pas assez de données pour afficher le Treemap.")

        with g2_col2:
            st.markdown("#### Top 10 des communes (selon filtres)")
            top_10 = df_cible.sort_values(by='Total_Filtre', ascending=False).head(10).sort_values(by='Total_Filtre', ascending=True)
            
            fig_top = px.bar(top_10, x='Total_Filtre', y='localisation', orientation='h', text_auto='.2s')
            fig_top.update_layout(
                xaxis_title="Population filtrée", 
                yaxis_title="",
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, b=0)
            )
            st.plotly_chart(fig_top, use_container_width=True)

        st.markdown("---")

        # --- SECTION 3 : LE TABLEAU DE DONNÉES ---
        st.markdown("### Tableau des Données Détaillées")
        
        # On prépare la liste des colonnes qu'on veut montrer à l'utilisateur
        colonnes_a_afficher = ['code_insee', 'localisation', 'Total_Filtre']
        
        # On ajoute dynamiquement les colonnes que l'utilisateur a cochées dans la Sidebar
        for age in ages_selectionnes:
            suffixe = dico_ages[age]
            if "Français" in nat_selectionnees: colonnes_a_afficher.append(f"FR{suffixe}")
            if "Étrangers" in nat_selectionnees: colonnes_a_afficher.append(f"ET{suffixe}")
            
        # On affiche le dataframe proprement
        st.dataframe(
            df_cible[colonnes_a_afficher].sort_values(by='Total_Filtre', ascending=False),
            use_container_width=True, # Prend toute la largeur de la page
            hide_index=True # Enlève les numéros de lignes inutiles (0, 1, 2...)
        )