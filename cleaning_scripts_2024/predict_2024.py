import pandas as pd
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
OUTPUT_CSV = BASE_DIR / "data_cleaned" / "2024" / "PREDICTIONS_FINALES_2024.csv"
MODEL_PATH = BASE_DIR / "models" / "best_model.joblib" 

# =========================================================
# 2. LECTURE DES DONNÉES SQLITE
# =========================================================
print(f"{C.BLUE}[1/4] CONNEXION À LA BASE DE DONNÉES...{C.END}")
if not DB_PATH.exists():
    sys.exit(1)
conn = sqlite3.connect(DB_PATH)
df_2024 = pd.read_sql("SELECT * FROM prediction_2024", conn)
print(f"  {C.GREEN} {len(df_2024):,} communes chargées.{C.END}\n")

# =========================================================
# 3. CHARGEMENT DU MODÈLE
# =========================================================
print(f"{C.BLUE}[2/4] CHARGEMENT DE L'INTELLIGENCE ARTIFICIELLE...{C.END}")
model = joblib.load(MODEL_PATH)
print(f"  {C.GREEN} Modèle ML chargé en mémoire avec succès.{C.END}\n")

# =========================================================
# 4. ALIGNEMENT DES DONNÉES (LE FIX MAGIQUE)
# =========================================================
print(f"{C.BLUE}[3/4] ALIGNEMENT DES COLONNES (BRIDGE 2022 -> 2024)...{C.END}")

cols_a_ignorer = ["code_insee_2024", "code_insee_2022", "nom_commune_2024", "annee", "code_insee"]
X_2024 = df_2024.drop(columns=[c for c in cols_a_ignorer if c in df_2024.columns], errors="ignore")

mapping = {
    "densite_asso_1000_hab": "nb_associations",
    "taux_creation_entreprises_1000_hab": "nb_creations_entreprises",
    "taux_chomage_15_64": "taux_chomage"
}
X_2024 = X_2024.rename(columns=mapping)

if "revenu_estime_2024" in X_2024.columns:
    X_2024["classe_revenu_pauvre"] = (X_2024["revenu_estime_2024"] < 20000).astype(int)
    X_2024["classe_revenu_moyen"] = ((X_2024["revenu_estime_2024"] >= 20000) & (X_2024["revenu_estime_2024"] <= 25000)).astype(int)
    X_2024["classe_revenu_riche"] = (X_2024["revenu_estime_2024"] > 25000).astype(int)

if hasattr(model, "feature_names_in_"):
    expected_cols = list(model.feature_names_in_)
    for col in expected_cols:
        if col not in X_2024.columns:
            X_2024[col] = 0
    X_2024 = X_2024[expected_cols]
    print(f"  {C.GREEN} Données parfaitement alignées sur les {len(expected_cols)} variables du modèle.{C.END}")
else:
    print(f"  {C.YELLOW} Impossible de lire les colonnes du modèle, on tente à l'aveugle...{C.END}")

# --- EXÉCUTION DES PRÉDICTIONS ---
predictions = model.predict(X_2024)

df_resultats = df_2024.copy()
df_resultats["prediction_politique_2024"] = predictions

# --- DÉCODAGE POUR POWER BI ---
traduction_partis = {
    0: "Centre",
    1: "Droite",
    2: "Extrême Droite",
    3: "Gauche",
    4: "Extrême Gauche"
}
# Création de la colonne lisible
df_resultats["Parti_Politique_Texte"] = df_resultats["prediction_politique_2024"].map(traduction_partis)

print(f"  {C.GREEN} Prédictions et décodage générés pour {len(predictions):,} communes.{C.END}\n")

# =========================================================
# 5. EXPORT DES RÉSULTATS
# =========================================================
print(f"{C.BLUE}[4/4] SAUVEGARDE DES RÉSULTATS...{C.END}")
df_resultats.to_sql("resultats_predictions_2024", conn, if_exists="replace", index=False)
conn.close()
print(f"  {C.GREEN} Table 'resultats_predictions_2024' créée dans SQLite.{C.END}")

df_resultats.to_csv(OUTPUT_CSV, sep=";", index=False, encoding="utf-8-sig")
file_size = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
print(f"  {C.GREEN} Fichier CSV généré ({file_size:.2f} MB).{C.END}")

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