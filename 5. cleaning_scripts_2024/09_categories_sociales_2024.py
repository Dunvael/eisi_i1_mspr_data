import pandas as pd
import numpy as np
from pathlib import Path
import sys

print(" Catégories Sociales")

# =========================================================
# 1. PARAMÈTRES ET CONFIGURATION
# =========================================================
BASE_DIR = Path(".")
FILE_CS_2022 = BASE_DIR / "data_cleaned" / "2022" / "03_categorie_sociale_2022_cleaned.csv"
FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"
FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "09_CS" / "09_categories_sociales_2024_clean.csv"

COEFFS_TENDANCE = {'agri': 0.813, 'cadres': 1.060, 'employes': 0.954, 'ouvriers': 0.952}

# =========================================================
# 2. CHARGEMENT
# =========================================================
try:
    df = pd.read_csv(FILE_CS_2022, sep=";")
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    print(" Données 2022 et référentiel chargés.")
except Exception as e:
    print(f" Erreur : {e}")
    sys.exit(1)

# =========================================================
# 3. NORMALISATION (Mise au standard 2024)
# =========================================================
# On s'assure que 'localisation' est bien un code INSEE propre sur 5 digits
df['code_insee_2024'] = df['localisation'].astype(str).str.strip().str.zfill(5)

cols_data = ['pourcentage_agri', 'pourcentage_cadres', 'pourcentage_employes', 'pourcentage_ouvriers']
for col in cols_data:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# =========================================================
# 4. PROJECTION 2024
# =========================================================
df['proj_agri'] = df['pourcentage_agri'] * COEFFS_TENDANCE['agri']
df['proj_cadres'] = df['pourcentage_cadres'] * COEFFS_TENDANCE['cadres']
df['proj_employes'] = df['pourcentage_employes'] * COEFFS_TENDANCE['employes']
df['proj_ouvriers'] = df['pourcentage_ouvriers'] * COEFFS_TENDANCE['ouvriers']

total_projete = df[['proj_agri', 'proj_cadres', 'proj_employes', 'proj_ouvriers']].sum(axis=1).replace(0, np.nan)

for col in cols_data:
    base_proj = col.replace('pourcentage_', 'proj_')
    df[col] = (df[base_proj] / total_projete * 100).fillna(0).round(2)

# =========================================================
# 5. MERGE SUR LE RÉFÉRENTIEL 2024
# =========================================================
df_final = pd.merge(df_ref[['code_insee_2024', 'nom_commune_2024']], 
                    df[['code_insee_2024'] + cols_data], 
                    on='code_insee_2024', how='left')


for col in cols_data:
    df_final[col] = df_final[col].fillna(df_final[col].median()).round(2)

df_final['annee'] = 2024

# =========================================================
# 6. EXPORT
# =========================================================
Path(FILE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

print(f"\n---  RÉSULTAT FINAL ---")
print(f"Fichier 2024 généré : {FILE_OUTPUT.name}")
print(df_final.head())