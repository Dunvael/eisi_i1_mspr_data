import pandas as pd
import numpy as np
import sqlite3
import joblib
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
print(f"{C.HEADER}{C.BOLD} DÉMARRAGE DU PIPELINE ML : PRÉDICTIONS POLITIQUES 2024{C.END}")
print(f"{C.HEADER}{C.BOLD}================================================================={C.END}\n")

# =========================================================
# 1. CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(".")
DB_PATH = BASE_DIR / "mspr_database.db"

OUTPUT_DIR = BASE_DIR / "data_cleaned" / "2024"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV = OUTPUT_DIR / "PREDICTIONS_FINALES_2024.csv"

MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "best_model.joblib"
ENCODER_PATH = MODEL_DIR / "label_encoder.joblib"

# =========================================================
# 2. LECTURE DES DONNÉES SQLITE
# =========================================================
print(f"{C.BLUE}[1/4] CONNEXION À LA BASE DE DONNÉES...{C.END}")
if not DB_PATH.exists():
    print(f"{C.RED}Erreur : Base de données introuvable ({DB_PATH}){C.END}")
    sys.exit(1)
conn = sqlite3.connect(DB_PATH)
df_2024 = pd.read_sql("SELECT * FROM prediction_2024", conn)
print(f"  {C.GREEN}✔ {len(df_2024):,} communes chargées.{C.END}\n")

# =========================================================
# 3. CHARGEMENT DU MODÈLE ET DES ARTEFACTS
# =========================================================
print(f"{C.BLUE}[2/4] CHARGEMENT DU MODÈLE IA...{C.END}")

if not MODEL_PATH.exists():
    print(f"{C.RED}❌ Modèle introuvable : {MODEL_PATH}{C.END}")
    sys.exit(1)

if not ENCODER_PATH.exists():
    print(f"{C.RED}❌ Encoder introuvable : {ENCODER_PATH}{C.END}")
    sys.exit(1)

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

print(f"  {C.GREEN}✔ Modèle et encoder chargés.{C.END}\n")
# =========================================================
# 4. ALIGNEMENT DES DONNÉES (LE FIX POUR RÉSULTATS LOGIQUES)
# =========================================================
# =========================================================
# 4. ALIGNEMENT DES DONNÉES
# =========================================================
print(f"{C.BLUE}[3/4] ALIGNEMENT DES COLONNES (BRIDGE 2022 -> 2024)...{C.END}")

cols_a_ignorer = [
    "code_insee_2024",
    "code_insee_2022",
    "nom_commune_2024",
    "annee",
    "code_insee",
    "classe_politique",
    "localisation",
    "nom_departement"
]

X_2024 = df_2024.drop(
    columns=[c for c in cols_a_ignorer if c in df_2024.columns],
    errors="ignore"
)

# =========================================================
# MAPPING ENTRE VARIABLES 2022 ET 2024
# =========================================================
mapping = {
    "densite_asso_1000_hab": "nb_associations",
    "taux_creation_entreprises_1000_hab": "nb_creations_entreprises",
    "taux_chomage_15_64": "taux_chomage",
    "taux_immigration_pct": "taux_immigration",
    "revenu_estime_2024": "revenu_median_final"
}

X_2024 = X_2024.rename(columns=mapping)

# =========================================================
# RECONSTRUCTION VARIABLES IMPORTANTES
# =========================================================
if "population" in X_2024.columns and "densite" in X_2024.columns:

    X_2024["population"] = pd.to_numeric(
        X_2024["population"],
        errors="coerce"
    )

    X_2024["densite"] = pd.to_numeric(
        X_2024["densite"],
        errors="coerce"
    )

    X_2024["superficie_km2"] = np.where(
        X_2024["densite"] > 0,
        X_2024["population"] / X_2024["densite"],
        np.nan
    )

# =========================================================
# CLASSES DE REVENUS
# =========================================================
if "revenu_median_final" in X_2024.columns:

    X_2024["revenu_median_final"] = pd.to_numeric(
        X_2024["revenu_median_final"],
        errors="coerce"
    )

    X_2024["classe_revenu_pauvre"] = (
        X_2024["revenu_median_final"] < 20000
    ).astype(int)

    X_2024["classe_revenu_moyen"] = (
        (X_2024["revenu_median_final"] >= 20000)
        &
        (X_2024["revenu_median_final"] <= 25000)
    ).astype(int)

    X_2024["classe_revenu_riche"] = (
        X_2024["revenu_median_final"] > 25000
    ).astype(int)

# =========================================================
# CONVERSION NUMÉRIQUE
# =========================================================
for col in X_2024.columns:
    X_2024[col] = pd.to_numeric(X_2024[col], errors="ignore")

# =========================================================
# ENCODAGE
# =========================================================
X_2024 = pd.get_dummies(
    X_2024,
    drop_first=False
)

# =========================================================
# ALIGNEMENT AUTOMATIQUE SUR LE MODÈLE
# =========================================================
expected_features = model.feature_names_in_

missing_cols = set(expected_features) - set(X_2024.columns)

if len(missing_cols) > 0:

    print(f"  {C.YELLOW}⚠ {len(missing_cols)} colonnes manquantes détectées.{C.END}")

    for col in missing_cols:
        X_2024[col] = 0

extra_cols = set(X_2024.columns) - set(expected_features)

if len(extra_cols) > 0:

    print(f"  {C.YELLOW}⚠ {len(extra_cols)} colonnes inutiles supprimées.{C.END}")

    X_2024 = X_2024.drop(columns=list(extra_cols))

# ordre EXACT du modèle
X_2024 = X_2024[expected_features]

print(f"  {C.GREEN}✔ Données parfaitement alignées sur le modèle ML.{C.END}\n")

# =========================================================
# 5. PRÉDICTIONS
# =========================================================
print(f"{C.BLUE}[4/4] EXÉCUTION DES PRÉDICTIONS...{C.END}")

predictions = model.predict(X_2024)

df_resultats = df_2024.copy()

df_resultats["prediction_politique_2024_code"] = predictions

try:

    df_resultats["Parti_Politique_Texte"] = encoder.inverse_transform(
        predictions
    )

except Exception as e:

    print(f"  {C.RED}⚠ Erreur lors du décodage : {e}{C.END}")

    df_resultats["Parti_Politique_Texte"] = predictions

print(f"  {C.GREEN}✔ Prédictions générées avec succès pour {len(predictions):,} communes.{C.END}\n")
# =========================================================
# SUPPRESSION COLONNE INUTILE
# =========================================================
df_resultats = df_resultats.drop(columns=["code_insee_2022"], errors="ignore")
# =========================================================
# 5. EXPORT DES RÉSULTATS
# =========================================================
# Arrondi pour alléger Power BI
for col in df_resultats.select_dtypes(include=['float64']).columns:
    df_resultats[col] = df_resultats[col].round(2)
colonnes = df_resultats.columns.tolist()
colonnes.insert(2, colonnes.pop(colonnes.index("nom_departement")))
df_resultats = df_resultats[colonnes]
print(f"{C.BLUE}SAUVEGARDE DES RÉSULTATS...{C.END}")
conn = sqlite3.connect(DB_PATH)
df_resultats.to_sql("resultats_predictions_2024", conn, if_exists="replace", index=False)
conn.close()
print(f"  {C.GREEN}✔ Table 'resultats_predictions_2024' créée dans SQLite.{C.END}")

df_resultats.to_csv(OUTPUT_CSV, sep=";", decimal=",", index=False, encoding="utf-8-sig")
file_size = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
print(f"  {C.GREEN}✔ Fichier CSV généré ({file_size:.2f} MB).{C.END}")

# =========================================================
# 6. RAPPORT FINAL
# =========================================================
exec_time = time.time() - start_time
print(f"\n{C.HEADER}{C.BOLD}================================================================={C.END}")
print(f"{C.HEADER}{C.BOLD} PRÉDICTIONS TERMINÉES - PIPELINE BIG DATA ACHEVÉ{C.END}")
print(f"{C.HEADER}{C.BOLD}================================================================={C.END}")
print(f" {C.BOLD}Temps de calcul ML{C.END}   : {exec_time:.2f} secondes")
print(f" {C.BOLD}Résultats finaux{C.END}     : {OUTPUT_CSV.name}")
print(f"{C.HEADER}{C.BOLD}================================================================={C.END}\n")