import pandas as pd
import unicodedata
import numpy as np
from pathlib import Path

BASE_DIR = Path(".")
FILE_2022 = BASE_DIR /  "2022_raw" / "0. Code INSEE 2022" / "commune_2022.csv"
FILE_2024 = BASE_DIR / "2024_raw" / "0. Code INSEE 2024" / "commune_2024.csv"
FILE_OUTPUT = BASE_DIR / "artifacts" / "referentiel_historique_22_24.csv"


def nettoyer_nom(nom):
    """Supprime les accents, tirets et apostrophes pour uniformiser les noms."""
    if pd.isna(nom):
        return nom
    nom = str(nom).upper()
    nom = ''.join(c for c in unicodedata.normalize('NFD', nom) if unicodedata.category(c) != 'Mn')
    nom = nom.replace('-', ' ').replace("'", " ")
    return nom.strip()

print("Construction du référentiel INSEE 2022 -> 2024 en cours...")

# séparateur (,) et à l'encodage (utf-8) pour le fichier 2024
df_ref_2022 = pd.read_csv(FILE_2022, dtype=str)
df_ref_2024 = pd.read_csv(FILE_2024, sep=",", dtype=str, encoding="utf-8")

# On remplace les valeurs vides par des chaînes de caractères vides
df_ref_2024['COMPARENT'] = df_ref_2024['COMPARENT'].fillna("")


# On crée la colonne "Vrai_Code_2024" :
# Si COMPARENT n'est pas vide (la commune a fusionné), on prend le code du parent.
# Sinon (commune normale), on garde son code 'COM'.
df_ref_2024['Vrai_Code_2024'] = np.where(
    df_ref_2024['COMPARENT'] != "", 
    df_ref_2024['COMPARENT'], 
    df_ref_2024['COM']
)

# --- 5. Nettoyage des noms pour la jointure ---
df_ref_2022['nom_clean'] = df_ref_2022['NCC'].apply(nettoyer_nom)
df_ref_2024['nom_clean'] = df_ref_2024['NCC'].apply(nettoyer_nom)

# --- 6. Jointure 2022 - 2024 ---
# On fusionne sur le nom propre et le département pour éviter les homonymes
df_pont = pd.merge(
    df_ref_2022[['COM', 'nom_clean', 'DEP']], 
    df_ref_2024[['COM', 'nom_clean', 'DEP', 'Vrai_Code_2024', 'TYPECOM']], 
    on=['nom_clean', 'DEP'], 
    suffixes=('_2022', '_2024')
)

# --- 7. Préparation et Export ---
# On ne garde que les colonnes utiles
df_export = df_pont[['COM_2022', 'Vrai_Code_2024', 'nom_clean', 'TYPECOM']].copy()
df_export.columns = ['Code_INSEE_2022', 'Code_INSEE_2024', 'Nom_Commune', 'Statut_2024']

# Création du dossier de destination s'il n'existe pas
FILE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df_export.to_csv(FILE_OUTPUT, index=False)

# --- 8. Affichage du bilan ---
fusions = len(df_export[df_export['Statut_2024'] == 'COMD'])
print(f"Succès ! {len(df_export)} communes traitées.")
print(f"Dont {fusions} communes de 2022 qui ont fusionné d'ici 2024 (elles ont pris le code de leur nouvelle commune).")
print(f"Fichier sauvegardé ici : {FILE_OUTPUT}")