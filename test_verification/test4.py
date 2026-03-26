import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(page_title="Dashboard Demographie & Activite", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 5px solid #2980b9;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CHARGEMENT DES DONNEES
# ==========================================
@st.cache_data
def load_data():
    # LA CORRECTION EST ICI : on force 'code_insee' et 'annee' en texte (str)
    df_22 = pd.read_csv("data_filtered/2022/CLEAN_4_Population_Activite_2022.csv", sep=";", dtype={'code_insee': str, 'annee': str})
    df_16 = pd.read_csv("data_filtered/2016/CLEAN_4_Population_Activite_2016.csv", sep=";", dtype={'code_insee': str, 'annee': str})
    
    df = pd.concat([df_16, df_22], ignore_index=True)
    
    # On s'assure que les colonnes de statistiques sont bien des nombres
    cols_num = df.columns[3:]
    df[cols_num] = df[cols_num].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    return df

df_all = load_data()

# Identification des colonnes
cols_age = df_all.columns[3:9].tolist()
cols_sec = df_all.columns[9:17].tolist()

lbl_age = ["0-14 ans", "15-29 ans", "30-44 ans", "45-59 ans", "60-74 ans", "75+ ans"]
lbl_sec = ["Agriculture", "Industrie", "Construction", "Commerce/Transp", "Admin/Sante", "Autres", "Services", "Non precise"]

# ==========================================
# 3. FILTRES (BARRE LATERALE)
# ==========================================
with st.sidebar:
    st.title("Filtres d'Analyse")
    
    liste_villes = sorted(df_all['localisation'].dropna().unique())
    choix_ville = st.selectbox("Commune ciblee :", ["Global (Toutes les communes)"] + list(liste_villes))
    choix_annee = st.selectbox("Annee :", ["Comparaison (2016 vs 2022)", "2022", "2016"])
    choix_age = st.selectbox("Tranche d'age :", ["Toutes les tranches"] + lbl_age)

# ==========================================
# 4. PREPARATION DES DONNEES FILTREES
# ==========================================
if choix_ville == "Global (Toutes les communes)":
    df_ville = df_all.groupby('annee')[cols_age + cols_sec].sum().reset_index()
else:
    df_ville = df_all[df_all['localisation'] == choix_ville]

def get_vals(year, columns):
    subset = df_ville[df_ville['annee'] == year]
    if not subset.empty:
        return subset[columns].values[0].tolist()
    return [0] * len(columns)

# Extraction avec des chaines de caracteres ("2016", "2022")
val_age_16 = get_vals("2016", cols_age)
val_age_22 = get_vals("2022", cols_age)
val_sec_16 = get_vals("2016", cols_sec)
val_sec_22 = get_vals("2022", cols_sec)

if choix_age != "Toutes les tranches":
    idx = lbl_age.index(choix_age)
    lbl_age_disp = [lbl_age[idx]]
    val_age_16_disp = [val_age_16[idx]]
    val_age_22_disp = [val_age_22[idx]]
else:
    lbl_age_disp, val_age_16_disp, val_age_22_disp = lbl_age, val_age_16, val_age_22

# ==========================================
# 5. KPIS
# ==========================================
st.title("Analyse de la Population et de l'Activite")

pop_16, pop_22 = sum(val_age_16_disp), sum(val_age_22_disp)
actifs_16, actifs_22 = sum(val_sec_16), sum(val_sec_22)

c1, c2, c3 = st.columns(3)
titre_pop = f"Population ({choix_age})" if choix_age != "Toutes les tranches" else "Population Totale"

if choix_annee == "2016":
    c1.metric(f"{titre_pop} (2016)", f"{int(pop_16):,} ".replace(",", " "))
    c2.metric("Personnes Actives (2016)", f"{int(actifs_16):,} ".replace(",", " "))
    c3.metric("Taux d'Activite", f"{(actifs_16/sum(val_age_16)*100):.1f}%" if sum(val_age_16) else "N/A")
elif choix_annee == "2022":
    c1.metric(f"{titre_pop} (2022)", f"{int(pop_22):,} ".replace(",", " "))
    c2.metric("Personnes Actives (2022)", f"{int(actifs_22):,} ".replace(",", " "))
    c3.metric("Taux d'Activite", f"{(actifs_22/sum(val_age_22)*100):.1f}%" if sum(val_age_22) else "N/A")
else:
    c1.metric(f"{titre_pop} (2022)", f"{int(pop_22):,} ".replace(",", " "), f"{((pop_22-pop_16)/pop_16*100):.2f}% vs 2016" if pop_16 else None)
    c2.metric("Personnes Actives (2022)", f"{int(actifs_22):,} ".replace(",", " "), f"{((actifs_22-actifs_16)/actifs_16*100):.2f}% vs 2016" if actifs_16 else None)
    c3.metric("Taux d'Activite", f"{(actifs_22/sum(val_age_22)*100):.1f}%" if sum(val_age_22) else "N/A")

st.write("---")

# ==========================================
# 6. ONGLETS ET GRAPHIQUES
# ==========================================
tab_demo, tab_eco, tab_data = st.tabs(["Demographie", "Secteurs d'Activite", "Base de Donnees"])

with tab_demo:
    st.subheader("Structure par Age")
    fig_age = go.Figure()
    
    if choix_annee in ["Comparaison (2016 vs 2022)", "2016"]:
        fig_age.add_trace(go.Bar(name='2016', x=lbl_age_disp, y=val_age_16_disp, marker_color='rgba(149, 165, 166, 0.8)'))
    if choix_annee in ["Comparaison (2016 vs 2022)", "2022"]:
        fig_age.add_trace(go.Bar(name='2022', x=lbl_age_disp, y=val_age_22_disp, marker_color='#2980b9'))
        
    fig_age.update_layout(barmode='group', xaxis_title="Tranches d'age", yaxis_title="Habitants")
    st.plotly_chart(fig_age, width="stretch")

with tab_eco:
    if choix_annee == "Comparaison (2016 vs 2022)":
        st.subheader("Bilan Net de l'Emploi par Secteur (2016 -> 2022)")
        diff_sec = [v22 - v16 for v22, v16 in zip(val_sec_22, val_sec_16)]
        df_diff = pd.DataFrame({"Secteur": lbl_sec, "Variation": diff_sec})
        
        fig_sec = px.bar(df_diff, x="Secteur", y="Variation", color="Variation", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig_sec, width="stretch")
    else:
        st.subheader(f"Repartition des Emplois ({choix_annee})")
        val_ref = val_sec_22 if choix_annee == "2022" else val_sec_16
        df_bar = pd.DataFrame({"Secteur": lbl_sec, "Effectifs": val_ref})
        
        fig_bar = px.bar(df_bar, x="Secteur", y="Effectifs", color="Secteur")
        st.plotly_chart(fig_bar, width="stretch")

with tab_data:
    st.subheader("Donnees Brutes")
    
    if choix_annee in ["Comparaison (2016 vs 2022)", "2022"]:
        st.markdown("**Annee 2022**")
        df_affiche_22 = df_all[df_all['annee'] == "2022"] if choix_ville == "Global (Toutes les communes)" else df_all[(df_all['annee'] == "2022") & (df_all['localisation'] == choix_ville)]
        st.dataframe(df_affiche_22.head(100), width="stretch", hide_index=True)
        
    if choix_annee in ["Comparaison (2016 vs 2022)", "2016"]:
        st.markdown("**Annee 2016**")
        df_affiche_16 = df_all[df_all['annee'] == "2016"] if choix_ville == "Global (Toutes les communes)" else df_all[(df_all['annee'] == "2016") & (df_all['localisation'] == choix_ville)]
        st.dataframe(df_affiche_16.head(100), width="stretch", hide_index=True)