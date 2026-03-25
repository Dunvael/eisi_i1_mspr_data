import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(layout="wide")
st.title("📊 Dashboard Activité & Démographie")

# ==========================================
# LOAD
# ==========================================
@st.cache_data
def load():
    df22 = pd.read_csv("data_filtered/activite/CLEAN_activite_2022.csv", sep=";")
    df16 = pd.read_csv("data_filtered/activite/CLEAN_activite_2016.csv", sep=";")
    return df22, df16

df_22, df_16 = load()

# ==========================================
# SIDEBAR
# ==========================================
ville = st.sidebar.selectbox(
    "Ville",
    ["France entière"] + sorted(df_22["localisation"].unique())
)

# ==========================================
# FILTER
# ==========================================
def get_data(df):
    if ville == "France entière":
        return df.drop(columns=["localisation"]).sum()
    return df[df["localisation"] == ville].iloc[0]

data_22 = get_data(df_22)
data_16 = get_data(df_16)

# ==========================================
# SAFE COLS
# ==========================================
cols_age = [c for c in df_22.columns if c.startswith("P_")]
cols_age = [c for c in cols_age if c in data_22.index and c in data_16.index]

cols_stat = [c for c in df_22.columns if c.startswith("C_")]
cols_stat = [c for c in cols_stat if c in data_22.index and c in data_16.index]

# ==========================================
# KPI
# ==========================================
pop22 = data_22[cols_age].sum()
pop16 = data_16[cols_age].sum()

evol = ((pop22 - pop16) / pop16) * 100 if pop16 != 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Population 2022", f"{int(pop22):,}".replace(",", " "))
c2.metric("Population 2016", f"{int(pop16):,}".replace(",", " "))
c3.metric("Evolution", f"{evol:.2f} %", delta=f"{evol:.2f}%")

# ==========================================
# AGE
# ==========================================
st.subheader("👥 Répartition âge")

df_age = pd.DataFrame({
    "Tranche": cols_age,
    "2016": data_16[cols_age].values,
    "2022": data_22[cols_age].values
})

fig = go.Figure()
fig.add_bar(x=df_age["Tranche"], y=df_age["2016"], name="2016")
fig.add_bar(x=df_age["Tranche"], y=df_age["2022"], name="2022")

fig.update_layout(barmode="group")
st.plotly_chart(fig, use_container_width=True)

# ==========================================
# SECTEURS
# ==========================================
st.subheader("🏭 Secteurs")

cols_sec = [c for c in cols_stat if "GSEC" in c]

df_sec = pd.DataFrame({
    "Secteur": cols_sec,
    "Valeur": data_22[cols_sec].values
})

fig2 = px.pie(df_sec, values="Valeur", names="Secteur", hole=0.4)
st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# STATUTS
# ==========================================
st.subheader("💼 Statuts")

cols_stat_simple = [c for c in cols_stat if "GSEC" not in c]

fig3 = go.Figure()
fig3.add_bar(x=cols_stat_simple, y=data_16[cols_stat_simple], name="2016")
fig3.add_bar(x=cols_stat_simple, y=data_22[cols_stat_simple], name="2022")

fig3.update_layout(barmode="group")
st.plotly_chart(fig3, use_container_width=True)

# ==========================================
# DEBUG
# ==========================================
with st.expander("🧪 Debug"):
    st.write("Colonnes communes :", len(set(df_22.columns) & set(df_16.columns)))
    st.dataframe(df_22.head())