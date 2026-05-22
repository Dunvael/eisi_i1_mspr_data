import pandas as pd
import sqlite3
import time
import os
from pathlib import Path
import sys

# --- Couleurs pour le terminal ---
class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

start_time = time.time()

print(f"\n{C.HEADER}{C.BOLD}================================================================={C.END}")
print(f"{C.HEADER}{C.BOLD}🚀 DÉMARRAGE DU PIPELINE ETL : MASTER DATASET 2024 (ADVANCED){C.END}")
print(f"{C.HEADER}{C.BOLD}================================================================={C.END}\n")

# =========================================================
# 1. CONFIGURATION
# =========================================================
BASE_DIR = Path(".")
DATA_CLEANED = BASE_DIR / "data_cleaned" / "2024"
OUTPUT_CSV = DATA_CLEANED / "MASTER_DATASET_ML_2024.csv"
DB_PATH = BASE_DIR / "mspr_database.db"

# =========================================================
# 2. CHARGEMENT DU RÉFÉRENTIEL
# =========================================================
print(f"{C.BLUE}[1/5] LECTURE DU RÉFÉRENTIEL...{C.END}")
ref_path = DATA_CLEANED / "00_referentiel_communes_22_24_clean.csv"
if not ref_path.exists():
    print(f"{C.RED}❌ Fichier introuvable : {ref_path}{C.END}")
    sys.exit(1)

df_master = pd.read_csv(ref_path, sep=";", dtype=str)
df_master["code_insee_2024"] = df_master["code_insee_2024"].str.zfill(5)
initial_rows = len(df_master)
print(f"  {C.GREEN}✔ Référentiel chargé : {initial_rows:,} communes (Ligne de base){C.END}\n")

# =========================================================
# 3. FUSION DES DATAMARTS
# =========================================================
print(f"{C.BLUE}[2/5] INTÉGRATION DES DATAMARTS...{C.END}")
datasets = [
    ("01_Densite_population/01.3_population_densite_2024_clean.csv", ["population", "densite"]),
    ("02_Criminalite/02_criminalite_diff_ndiff_2024_cleaned.csv", ["taux_cambriolages_logement", "taux_violences_intrafamiliales"]),
    ("03_Demographie/03_tranches_age_2024_clean.csv", ["pct_jeunes", "pct_seniors", "age_median"]),
    ("04_Revenus/04_revenus_2024_estim_clean.csv", ["revenu_estime_2024"]),
    ("05_Chomage/05_chomage_2024_clean.csv", ["taux_chomage_15_64"]),
    ("06_Associations/06_associations_2024_clean.csv", ["densite_asso_1000_hab"]),
    ("07_Entreprises/07_creations_entreprises_2024_clean.csv", ["taux_creation_entreprises_1000_hab"]),
    ("08_Immigration/08_immigration_2024_clean.csv", ["taux_immigration_pct"]),
    ("09_CS/09_categories_sociales_2024_clean.csv", ["pourcentage_agri", "pourcentage_cadres", "pourcentage_employes", "pourcentage_ouvriers"])
]

for file_rel_path, cols in datasets:
    path = DATA_CLEANED / file_rel_path
    if path.exists():
        df_temp = pd.read_csv(path, sep=";", dtype=str)
        df_temp["code_insee_2024"] = df_temp["code_insee_2024"].str.zfill(5)
        
        # Audit qualité
        doublons_avant = len(df_temp)
        df_temp = df_temp.drop_duplicates(subset=['code_insee_2024'])
        doublons_retires = doublons_avant - len(df_temp)
        
        df_master = pd.merge(df_master, df_temp[["code_insee_2024"] + cols], on="code_insee_2024", how="left")
        
        msg_doublon = f" (⚠️ {doublons_retires} doublons retirés)" if doublons_retires > 0 else ""
        print(f"  {C.GREEN}✔ {file_rel_path.split('/')[0]:<25} intégré{msg_doublon}{C.END}")
    else:
        print(f"  {C.RED}❌ Ignoré (introuvable) : {file_rel_path}{C.END}")

# =========================================================
# 4. NETTOYAGE & DATA QUALITY
# =========================================================
print(f"\n{C.BLUE}[3/5] DATA QUALITY & IMPUTATION...{C.END}")
numeric_cols = [c for c in df_master.columns if c not in ["code_insee_2024", "nom_commune_2024", "annee"]]

# Typage
df_master[numeric_cols] = df_master[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Audit des NaN avant nettoyage
nan_total = df_master.isna().sum().sum()
if nan_total > 0:
    print(f"  {C.YELLOW}⚠ {nan_total:,} valeurs manquantes détectées.{C.END}")
    print(f"  {C.CYAN}⚙ Application de l'imputation par la médiane nationale...{C.END}")
    df_master[numeric_cols] = df_master[numeric_cols].fillna(df_master[numeric_cols].median())
    print(f"  {C.GREEN}✔ Imputation réussie. Dataset 100% complet pour le ML.{C.END}")
else:
    print(f"  {C.GREEN}✔ Aucune valeur manquante. Qualité optimale.{C.END}")

# =========================================================
# 5. EXPORT CSV & SQLITE
# =========================================================
print(f"\n{C.BLUE}[4/5] SAUVEGARDE & EXPORT...{C.END}")

# CSV
df_master.to_csv(OUTPUT_CSV, sep=";", index=False, encoding="utf-8-sig")
file_size_mb = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
print(f"  {C.GREEN}✔ Fichier CSV généré ({file_size_mb:.2f} MB){C.END}")

# SQLite
try:
    conn = sqlite3.connect(DB_PATH)
    df_master.to_sql("prediction_2024", conn, if_exists="replace", index=False)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM prediction_2024")
    row_count = cursor.fetchone()[0]
    conn.close()
    print(f"  {C.GREEN}✔ Base SQLite mise à jour : {row_count:,} entrées dans 'prediction_2024'.{C.END}")
except Exception as e:
    print(f"  {C.RED}❌ Erreur SQLite : {e}{C.END}")

# =========================================================
# 6. RAPPORT D'EXÉCUTION
# =========================================================
exec_time = time.time() - start_time
memory_usage = df_master.memory_usage(deep=True).sum() / (1024 * 1024)

print(f"\n{C.HEADER}{C.BOLD}================================================================={C.END}")
print(f"{C.HEADER}{C.BOLD}📊 RAPPORT D'AUDIT FINAL - PIPELINE RÉUSSI{C.END}")
print(f"{C.HEADER}{C.BOLD}================================================================={C.END}")
print(f" {C.BOLD}Temps d'exécution{C.END}      : {exec_time:.2f} secondes")
print(f" {C.BOLD}Mémoire RAM allouée{C.END}    : {memory_usage:.2f} MB")
print(f" {C.BOLD}Communes consolidées{C.END}   : {len(df_master):,}")
print(f" {C.BOLD}Variables ML générées{C.END}  : {df_master.shape[1]}")
print(f" {C.BOLD}Format de Sortie{C.END}       : CSV (Power BI) + SQLite (Machine Learning)")
print(f"{C.HEADER}{C.BOLD}================================================================={C.END}\n")