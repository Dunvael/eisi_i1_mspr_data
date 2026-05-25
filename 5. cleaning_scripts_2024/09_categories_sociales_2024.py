import pandas as pd
import numpy as np
from pathlib import Path
import sys

print("Catégories Sociales")


# 1. PARAMÈTRES ET CONFIGURATION

BASE_DIR = Path(".")
FILE_CS_2022 = BASE_DIR / "data_cleaned" / "2022" / "03_categorie_sociale_2022_cleaned.csv"
FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"
FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "09_CS" / "09_categories_sociales_2024_clean.csv"

# Coefficients de tendance structurelle (projection 2022 → 2024)
COEFFS_TENDANCE = {'agri': 0.813, 'cadres': 1.060, 'employes': 0.954, 'ouvriers': 0.952}


# 2. CHARGEMENT DES DONNÉES

try:
    df = pd.read_csv(FILE_CS_2022, sep=";")
    df_ref = pd.read_csv(FILE_REF, sep=";", dtype=str)
    print(" Données 2022 et référentiel chargés.")
except Exception as e:
    print(f" Erreur : {e}")
    sys.exit(1)


# 3. PRÉPARATION DES CLÉS 

cols_data = ['pourcentage_agri', 'pourcentage_cadres', 'pourcentage_employes', 'pourcentage_ouvriers']

# Conversion en numérique
for col in cols_data:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Clé 1 : Nettoyage pour le Code INSEE
df['key_code'] = df['localisation'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(5)
df_ref['key_code'] = df_ref['code_insee_2024'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(5)

# Clé 2 : Nettoyage pour le Nom de Commune
df['key_nom'] = df['localisation'].astype(str).str.upper().str.strip()
df_ref['key_nom'] = df_ref['nom_commune_2024'].astype(str).str.upper().str.strip()


# 4. Application des tendances par catégorie


df['proj_agri'] = df['pourcentage_agri'] * COEFFS_TENDANCE['agri']
df['proj_cadres'] = df['pourcentage_cadres'] * COEFFS_TENDANCE['cadres']
df['proj_employes'] = df['pourcentage_employes'] * COEFFS_TENDANCE['employes']
df['proj_ouvriers'] = df['pourcentage_ouvriers'] * COEFFS_TENDANCE['ouvriers']

total_projete = df[['proj_agri', 'proj_cadres', 'proj_employes', 'proj_ouvriers']].sum(axis=1).replace(0, np.nan)

for col in cols_data:
    base_proj = col.replace('pourcentage_', 'proj_')
    df[col] = (df[base_proj] / total_projete * 100).round(2)


# 5. FUSION RÉFÉRENTIEL

# Fusion par code INSEE
df_merge_code = pd.merge(df_ref[['code_insee_2024', 'nom_commune_2024', 'key_code']], 
                         df[['key_code'] + cols_data], 
                         on='key_code', how='left')

# Fusion fallback par nom commune
df_merge_nom = pd.merge(df_ref[['code_insee_2024', 'nom_commune_2024', 'key_nom']], 
                        df[['key_nom'] + cols_data], 
                        on='key_nom', how='left')


df_final = df_merge_code[['code_insee_2024', 'nom_commune_2024']].copy()
for col in cols_data:
    df_final[col] = df_merge_code[col].combine_first(df_merge_nom[col])


# Remplissage : MÉDIANE DÉPARTEMENTALE

print("Imputation des valeurs manquantes par la médiane départementale...")

# 1. On extrait le numéro de département
df_final['code_dept'] = df_final['code_insee_2024'].astype(str).str[:2]

for col in cols_data:
    # 2. On calcule la médiane spécifique au département
    df_final['mediane_dept'] = df_final.groupby('code_dept')[col].transform('median')
    
    # 3. On calcule la médiane nationale 
    mediane_nationale = df_final[col].median()
    
    # 4. Remplacement : Médiane Dept d'abord, puis Nationale
    df_final[col] = df_final[col].fillna(df_final['mediane_dept']).fillna(mediane_nationale).round(2)

# 5. Nettoyage des colonnes
df_final = df_final.drop(columns=['code_dept', 'mediane_dept'])

df_final['annee'] = 2024


# 6. EXPORT

Path(FILE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

print(f"\n--- RÉSULTAT ---")
print(f"Fichier 2024 généré : {FILE_OUTPUT.name}")
print(df_final.head())