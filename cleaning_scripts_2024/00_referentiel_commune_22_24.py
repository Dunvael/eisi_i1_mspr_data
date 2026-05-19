import pandas as pd
from pathlib import Path
import sys

print("Création du Référentiel  communes 2022-2024")

# =========================================================
# 1. CONFIGURATION
# =========================================================
BASE_DIR = Path(".")
FILE_INSEE_PASSAGE = BASE_DIR / "data_raw" / "2024_raw" / "0. Code INSEE 2024" / "table_passage_annuelle_2024.xlsx"
FILE_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"

def nettoyer_et_monitorer():
    if not FILE_INSEE_PASSAGE.exists():
        print(f"Fichier introuvable : {FILE_INSEE_PASSAGE}")
        sys.exit(1)

    print("Chargement des données...")
    df_raw = pd.read_excel(FILE_INSEE_PASSAGE, dtype=str, header=5)
    df_raw.columns = df_raw.columns.astype(str).str.strip()

    lignes_depart = len(df_raw)
    
    col_nom = "LIBGEO_2024" if "LIBGEO_2024" in df_raw.columns else "LIBGEO"
    df = df_raw[["CODGEO_2022", "CODGEO_2024", col_nom]].copy()

    # Nettoyage 
    df["CODGEO_2022"] = df["CODGEO_2022"].astype(str).str.strip().str.zfill(5)
    df["CODGEO_2024"] = df["CODGEO_2024"].astype(str).str.strip().str.zfill(5)
    df[col_nom] = df[col_nom].astype(str).str.strip().str.upper()

    # ---------------------------------------------------------
    #  Suppression des Arrondissements 
    # ---------------------------------------------------------
    masque_arrondissements = (
        df["CODGEO_2024"].str.startswith("751") | 
        df["CODGEO_2024"].str.startswith("132") | 
        df["CODGEO_2024"].str.startswith("693")
    )
    nb_arrondissements = masque_arrondissements.sum()
    df = df[~masque_arrondissements] # On ne garde que ce qui n'est PAS un arrondissement
    # On retire les doublons 
    df = df.drop_duplicates()

    # ---------------------------------------------------------
    # Fusions de communes
    # ---------------------------------------------------------
    comptage_fusions = df.groupby("CODGEO_2024")["CODGEO_2022"].nunique()
    communes_fusionnees = comptage_fusions[comptage_fusions > 1]
    nb_fusions = len(communes_fusionnees)
    nb_anciennes_communes_absorbees = communes_fusionnees.sum()

    # On cherche les vrais NaN, mais aussi les chaines "nan", "0", ou vides
    masque_nan = df.isna() | (df == "nan") | (df == "0") | (df == "00000") | (df == "")
    nb_nan_total = masque_nan.sum().sum()


    lignes_fin = len(df)
    

    lignes_incompletes = masque_nan.any(axis=1).sum()
    taux_parfait = ((lignes_fin - lignes_incompletes) / lignes_fin) * 100 if lignes_fin > 0 else 0

    # Renommage 
    df = df.rename(columns={
        "CODGEO_2022": "code_insee_2022",
        "CODGEO_2024": "code_insee_2024",
        col_nom: "nom_commune_2024"
    })

    # Sauvegarde
    Path(FILE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(FILE_OUTPUT, sep=";", index=False, encoding="utf-8-sig")

    # =========================================================
    # 6. AFFICHAGE 
    # =========================================================
    print("\n" + "="*50)
    print(" RAPPORT DE QUALITÉ DES DONNÉES")
    print("="*50)
    print(f"(Fichier brut) : {lignes_depart}")
    print(f"  Arrondissements supprimés : {nb_arrondissements}")
    print(f"(Référentiel)  : {lignes_fin}")
    print("-" * 50)
    print(f" Nouvelles Communes (issues de fusions) : {nb_fusions}")
    print(f" Anciens villages absorbés par fusion   : {nb_anciennes_communes_absorbees}")
    print("-" * 50)
    print(f"  Valeurs manquantes ou zéros (NaN)      : {nb_nan_total}")
    print(f" TAUX DE PERFECTION       : {taux_parfait:.2f} %")
    print("="*50 + "\n")
    
    if nb_nan_total > 0:
        print(" référentiel contient des valeurs manquantes.")
    else:
        print("référentiel est 100% propre, ")
        

if __name__ == "__main__":
    nettoyer_et_monitorer()