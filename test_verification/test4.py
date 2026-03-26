import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# Charger les données
BASE_DIR = Path(".") / "data_filtered"
year = 2022
file = BASE_DIR / str(year) / f"CLEAN_4_Population_Activite_{year}.csv"
df = pd.read_csv(file, sep=";", encoding="utf-8-sig")

# Sidebar - filtres
st.sidebar.title("Filtres")
villes = st.sidebar.multiselect("Sélectionner ville(s):", sorted(df['localisation'].unique()))
secteurs = [c for c in df.columns if c not in ['code_insee', 'localisation', 'annee']]

# Filtrer les données
df_filtered = df.copy()
if villes:
    df_filtered = df_filtered[df_filtered['localisation'].isin(villes)]

# Total population par ville
df_filtered['Total'] = df_filtered[secteurs].sum(axis=1)
top10 = df_filtered.nlargest(10, 'Total')

# Graphique Top 10 villes
st.header(f"Top 10 villes par population totale {year}")
fig = px.bar(top10, x='localisation', y='Total', text='Total')
fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
st.plotly_chart(fig, use_container_width=True)

# Heatmap secteurs / villes
st.header(f"Répartition population par secteur et ville {year}")
df_melt = df_filtered.melt(id_vars=['localisation'], value_vars=secteurs,
                           var_name='Secteur', value_name='Population')
fig2 = px.density_heatmap(df_melt, x='localisation', y='Secteur', z='Population',
                          color_continuous_scale='Viridis')
st.plotly_chart(fig2, use_container_width=True)