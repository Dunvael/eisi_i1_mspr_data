import pandas as pd
from pathlib import Path

# --- 1. Chemins des fichiers ---
BASE_DIR = Path(".")
FILE_REVENU = BASE_DIR / "data_cleaned" / "2022" / "01_revenus_median_2021_cleaned.csv"
FILE_CHOMAGE = BASE_DIR / "data_cleaned" / "2022" / "02_taux_chomage_2022_cleaned.csv"
FILE_PONT = BASE_DIR / "artifacts" / "referentiel_historique_22_24.csv"
FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "01_revenus_median_2024_estime.csv"

ALPHA = 0.10  

print("⏳ Estimation des revenus 2024 (AVEC les vrais Codes INSEE)...")

# --- 2. Chargement des données ---
df_rev = pd.read_csv(FILE_REVENU, sep=";", dtype=str)
df_chom = pd.read_csv(FILE_CHOMAGE, sep=";", dtype=str)
df_pont = pd.read_csv(FILE_PONT, dtype=str)

# Conversion numérique de sécurité
df_rev['revenu_median'] = pd.to_numeric(df_rev['revenu_median'], errors='coerce')
df_chom['taux_chomage'] = pd.to_numeric(df_chom['taux_chomage'], errors='coerce')

# --- 3. Jointures Parfaites (Grâce au Code INSEE) ---
df_merged = pd.merge(df_pont, df_rev, left_on='Code_INSEE_2022', right_on='code_insee', how='inner')
df_merged = pd.merge(df_merged, df_chom[['code_insee', 'taux_chomage']], on='code_insee', how='inner')

# --- 4. Le Calcul de votre Modèle ---
df_merged['chomage_norm'] = df_merged['taux_chomage'] / 25.0
df_merged['revenu_estime_2024'] = df_merged['revenu_median'] * (1.12 - (ALPHA * df_merged['chomage_norm']))

# --- 5. GESTION DES FUSIONS DE COMMUNES ---
df_final = df_merged.groupby(['Code_INSEE_2024', 'Nom_Commune'], as_index=False)['revenu_estime_2024'].mean()

df_final['revenu_estime_2024'] = df_final['revenu_estime_2024'].round(0)
df_final = df_final.rename(columns={'Code_INSEE_2024': 'code_insee', 'Nom_Commune': 'localisation'})

# --- 6. Exportation ---
FILE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(FILE_OUTPUT, index=False, sep=";", encoding="utf-8-sig")

print(f"✅ Succès ! {len(df_final)} revenus estimés pour 2024.")
print(f"Fichier sauvegardé ici : {FILE_OUTPUT}")