import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import missingno as msno
import os


# 1. CONFIGURATION

st.set_page_config(page_title="Visuels Chômage", layout="wide")
st.title("Analyse du Chômage 2024")


# 2. CHARGEMENT DES DONNÉES

@st.cache_data
def load_data():
    file_path = "data_cleaned/2024/05_Chomage/05_chomage_2024_clean.csv"
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path, sep=";")

df = load_data()

if df is None:
    st.error(" Erreur : Le fichier est introuvable. Vérifie ton chemin.")
else:
    # Gestion dynamique du nom de la colonne
    if 'taux_chomage_15_64' in df.columns and 'taux_chomage' not in df.columns:
        df = df.rename(columns={'taux_chomage_15_64': 'taux_chomage'})

    colonne_cible = 'taux_chomage'

    if colonne_cible not in df.columns:
        st.error(" Erreur : La colonne de taux de chômage est introuvable dans le fichier.")
    else:
        
        
        # 3. GRAPHIQUE 1 : COMPLÉTUDE 
        
        st.subheader(" Graphique de complétude")
        
        # Sélection des colonnes présentes
        colonnes_visibles = [col for col in df.columns if col in ['code_insee_2024', colonne_cible, 'annee']]
        if not colonnes_visibles:
            colonnes_visibles = df.columns[:3].tolist() 

        fig_msno = plt.figure(figsize=(7, 5))
        ax_msno = fig_msno.add_subplot(111)

        # Génération du bar-chart gris
        msno.bar(df[colonnes_visibles], ax=ax_msno, fontsize=11, color=(0.4, 0.4, 0.4))
        plt.title("Nombre de valeurs manquantes - taux de chômage", fontsize=12, pad=20)
        plt.tight_layout()
        
        st.pyplot(fig_msno)

        st.divider() # Ligne de séparation visuelle

        
        # 4. GRAPHIQUE 2 : DISTRIBUTION DU TAUX DE CHÔMAGE
        
        st.subheader("Histogramme de distribution")

        fig_hist = plt.figure(figsize=(7, 5))


        plt.hist(df[colonne_cible].dropna(), bins=45, color="#1f77b4", edgecolor="none")

        plt.title("Distribution du taux de chômage", fontsize=12, pad=15)
        plt.xlabel("Taux de chômage (%)", fontsize=10)

        # Configuration de la grille
        plt.grid(True, which='both', linestyle='-', alpha=0.7)
        plt.tight_layout()

        # Affichage via Streamlit
        st.pyplot(fig_hist)