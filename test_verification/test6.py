import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(page_title="Dashboard Activité & Immigration", page_icon="", layout="wide")

# ==========================================
# 2. CHARGEMENT DES DONNÉES
# ==========================================
@st.cache_data
def load_data():
    chemin_fichier = Path("data_filtered/2022/CLEAN_6_Sexe_Nationalite_Activite_2022.csv")
    if chemin_fichier.exists():
        return pd.read_csv(chemin_fichier, sep=";", decimal=".")
    return None

df = load_data()

# ==========================================
# 3. INTERFACE & FILTRES DYNAMIQUES
# ==========================================
if df is None:
    st.error("⚠️ Fichier introuvable. Avez-vous bien lancé le script 06 d'extraction ?")
else:
    # --- BARRE LATÉRALE ---
    st.sidebar.title("Filtres Socio-Économiques")
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### Localisation")
    vue_globale = st.sidebar.checkbox("Toutes les communes (Vue Globale)", value=False)
    
    liste_communes = df['localisation'].sort_values().unique()
    
    if vue_globale:
        df_cible = df.copy()
        titre_localisation = "Vue Globale (France détaillée)"
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
    
    dico_nat = {"Français": "FR", "Étrangers": "ET"}
    nat_selectionnees = st.sidebar.multiselect("Nationalité :", options=list(dico_nat.keys()), default=list(dico_nat.keys()))

    dico_act = {
        "En emploi": "_EMPLOI", 
        "Chômeurs": "_CHOMEUR", 
        "Retraités": "_RETRAITE", 
        "Étudiants": "_ETUDIANT", 
        "Au foyer": "_AU_FOYER", 
        "Autres inactifs": "_AUTRE_INACTIF"
    }
    act_selectionnees = st.sidebar.multiselect("Statut d'activité :", options=list(dico_act.keys()), default=list(dico_act.keys()))

    # ==========================================
    # 4. CALCULS BASÉS SUR LES FILTRES
    # ==========================================
    if len(act_selectionnees) == 0 or len(nat_selectionnees) == 0 or (not vue_globale and len(communes_selectionnees) == 0):
        st.warning("⚠️ Veuillez sélectionner au moins une localisation, une nationalité et un statut.")
    else:
        total_pop_filtree = 0
        df_cible['Total_Filtre'] = 0 
        
        # Pour les KPIs économiques (Indépendants des filtres d'activité pour toujours avoir du sens)
        tot_emploi = 0
        tot_chomeur = 0
        
        for nat in nat_selectionnees:
            pref = dico_nat[nat]
            tot_emploi += df_cible[f"{pref}_EMPLOI"].sum()
            tot_chomeur += df_cible[f"{pref}_CHOMEUR"].sum()
            
            for act in act_selectionnees:
                suff = dico_act[act]
                col_name = f"{pref}{suff}"
                df_cible['Total_Filtre'] += df_cible[col_name]
                total_pop_filtree += df_cible[col_name].sum()

        # Calcul du Taux de Chômage : (Chômeurs / Population Active) * 100
        # Population active = En emploi + Chômeurs
        pop_active = tot_emploi + tot_chomeur
        taux_chomage = (tot_chomeur / pop_active * 100) if pop_active > 0 else 0

        # ==========================================
        # 5. AFFICHAGE DU DASHBOARD
        # ==========================================
        st.title(f"Analyse de l'Activité : {titre_localisation}")
        st.markdown(f"*(Population de 15 ans ou plus, selon vos critères de nationalité)*")
        
        # --- KPIs STRATÉGIQUES ---
        st.markdown("### Indicateurs Économiques (Sur la nationalité sélectionnée)")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Population Filtrée", f"{total_pop_filtree:,.0f}".replace(',', ' '))
        col2.metric("En Emploi", f"{tot_emploi:,.0f}".replace(',', ' '))
        col3.metric("Chômeurs", f"{tot_chomeur:,.0f}".replace(',', ' '))
        
        # Un KPI de taux de chômage en rouge si > 10%, vert sinon
        color_chomage = "normal" if taux_chomage < 10 else "inverse"
        col4.metric("Taux de Chômage", f"{taux_chomage:.1f} %", delta_color=color_chomage)
        
        st.markdown("---")

        # --- GRAPHIQUES ---
        g1_col1, g1_col2 = st.columns(2)

        with g1_col1:
            st.markdown("#### Répartition par statut et nationalité")
            # Graphique en barres empilées pour voir la proportion FR/ET dans chaque statut
            bar_data = []
            for act in act_selectionnees:
                if "Français" in nat_selectionnees:
                    bar_data.append({"Statut": act, "Nationalité": "Français", "Valeur": df_cible[f"FR{dico_act[act]}"].sum()})
                if "Étrangers" in nat_selectionnees:
                    bar_data.append({"Statut": act, "Nationalité": "Étrangers", "Valeur": df_cible[f"ET{dico_act[act]}"].sum()})
            
            if bar_data:
                df_bar = pd.DataFrame(bar_data)
                fig_bar = px.bar(df_bar, x="Statut", y="Valeur", color="Nationalité", barmode="group", color_discrete_map={"Français": "#1f77b4", "Étrangers": "#ff7f0e"})
                fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=0))
                st.plotly_chart(fig_bar, use_container_width=True)

        with g1_col2:
            st.markdown("#### Poids des statuts d'activité")
            pie_data = [{"Statut": act, "Valeur": sum([df_cible[f"{dico_nat[nat]}{dico_act[act]}"].sum() for nat in nat_selectionnees])} for act in act_selectionnees]
            df_pie = pd.DataFrame(pie_data)
            
            fig_pie = px.pie(df_pie, values='Valeur', names='Statut', hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(margin=dict(t=30, b=0), showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        # --- DEUXIÈME SECTION : TOP 10 ET TABLEAU ---
        g2_col1, g2_col2 = st.columns([1, 2]) # Le tableau prendra plus de place (ratio 1:2)

        with g2_col1:
            st.markdown("#### Top 10 des communes")
            top_10 = df_cible.sort_values(by='Total_Filtre', ascending=False).head(10).sort_values(by='Total_Filtre', ascending=True)
            fig_top = px.bar(top_10, x='Total_Filtre', y='localisation', orientation='h', text_auto='.2s', color_discrete_sequence=['#2ca02c'])
            fig_top.update_layout(xaxis_title="Volume filtré", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=0))
            st.plotly_chart(fig_top, use_container_width=True)

        with g2_col2:
            st.markdown("### Données Brutes Interactives")
            colonnes_a_afficher = ['code_insee', 'localisation', 'Total_Filtre']
            for nat in nat_selectionnees:
                for act in act_selectionnees:
                    colonnes_a_afficher.append(f"{dico_nat[nat]}{dico_act[act]}")
            
            st.dataframe(
                df_cible[colonnes_a_afficher].sort_values(by='Total_Filtre', ascending=False),
                use_container_width=True,
                hide_index=True,
                height=350 # Fixe la hauteur pour s'aligner avec le graphique d'à côté
            )