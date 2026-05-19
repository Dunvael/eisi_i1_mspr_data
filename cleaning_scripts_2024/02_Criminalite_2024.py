import pandas as pd
from pathlib import Path
import sys

print("Nettoyage criminalité 2024")

# =========================================================
# 1. CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(".")

FILE_REF = BASE_DIR / "data_cleaned" / "2024" / "00_referentiel_communes_22_24_clean.csv"
FILE_DATA = BASE_DIR / "data_raw" / "2024_raw" / "2. Criminalite" / "criminalite_2024.csv"
DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2024" / "02_Criminalite"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)

def clean_criminalite_all(year=2024):
    if not FILE_REF.exists():
        print(f"Référentiel introuvable : {FILE_REF}")
        sys.exit(1)
    if not FILE_DATA.exists():
        print(f"Données introuvables : {FILE_DATA}")
        sys.exit(1)

    # =========================================================
    # 2. LECTURE DES DONNÉES
    # =========================================================
    ref = pd.read_csv(FILE_REF, sep=";", dtype=str)

    print(f" Lecture des données de criminalité {year}...")
    if FILE_DATA.suffix == '.parquet':
        df = pd.read_parquet(FILE_DATA)
    else:
        df = pd.read_csv(FILE_DATA, sep=";", dtype=str)

    col_geo_source = "CODGEO_2025" if "CODGEO_2025" in df.columns else "CODGEO"
    df[col_geo_source] = df[col_geo_source].astype(str).str.strip().str.zfill(5)

    # =========================================================
    # 3. MAPPING GÉOGRAPHIQUE  RÉFÉRENTIEL
    # =========================================================
    print("Application du mapping géographique...")
    df = df.merge(ref, left_on=col_geo_source, right_on="code_insee_2024", how="inner")

    df["code_insee_final"] = df["code_insee_2024"].fillna(df[col_geo_source])

    # =========================================================
    # 4. FILTRAGE 
    # =========================================================
    indicateurs_gardes = [
        "Violences physiques intrafamiliales",
        "Violences sexuelles",
        "Vols avec armes",
        "Vols violents sans arme",
        "Cambriolages de logement",
        "Vols de véhicule",
        "Destructions et dégradations volontaires",
        "Usage de stupéfiants",
        "Trafic de stupéfiants"
    ]

    df["annee"] = df["annee"].astype(str)
    df = df[
        (df["annee"] == str(year)) &
        (df["indicateur"].isin(indicateurs_gardes))
    ].copy()

    # =========================================================
    # 5. GESTION DU TAUX FINAL 
    # =========================================================
    # Récupération des données masquées (ndiff)
    df["taux_final"] = df["taux_pour_mille"].fillna(df["complement_info_taux"])

    df["taux_final"] = df["taux_final"].astype(str).str.replace(',', '.')
    df["taux_final"] = pd.to_numeric(df["taux_final"], errors="coerce")

    # =========================================================
    # 6. PIVOT DES DONNÉES
    # =========================================================
    print("Pivot de la table...")
    df_pivot = df.pivot_table(
        index=["code_insee_final", "annee"],
        columns="indicateur",
        values="taux_final",
        aggfunc="mean" # Moyenne du taux si des communes ont fusionné
    ).reset_index()

    # =========================================================
    # 7. RENOMMAGE 
    # =========================================================
    df_pivot = df_pivot.rename(columns={
        "code_insee_final": "code_insee_2024",
        "Violences physiques intrafamiliales": "taux_violences_intrafamiliales",
        "Violences sexuelles": "taux_violences_sexuelles",
        "Vols avec armes": "taux_vols_avec_armes",
        "Vols violents sans arme": "taux_vols_violents_sans_arme",
        "Cambriolages de logement": "taux_cambriolages_logement",
        "Vols de véhicule": "taux_vols_vehicule",
        "Destructions et dégradations volontaires": "taux_degradations",
        "Usage de stupéfiants": "taux_usage_stupefiants",
        "Trafic de stupéfiants": "taux_trafic_stupefiants"
    })

    df_pivot = df_pivot.merge(ref[["code_insee_2024", "nom_commune_2024"]].drop_duplicates(), on="code_insee_2024", how="left")
    
    cols = df_pivot.columns.tolist()
    cols.insert(1, cols.pop(cols.index("nom_commune_2024")))
    df_pivot = df_pivot[cols]

    # =========================================================
    # 8. EXPORT ET DASHBOARD
    # =========================================================
    fichier_sortie = DIR_OUTPUT / f"02_criminalite_diff_ndiff_{year}_cleaned.csv"
    df_pivot.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")

    print("\n" + "="*50)
    print(f" RAPPORT : CRIMINALITÉ {year}")
    print("="*50)
    print(f"Fichier créé : {fichier_sortie.name}")
    print(f"\n Shape finale : {df_pivot.shape}")

    print("\n NaN count par indicateur (Certaines communes n'ont pas de données pour certains crimes) :")
    print(df_pivot.isna().sum())

    print("\n Pourcentage de NaN (%) :")
    print((df_pivot.isna().mean() * 100).round(2))

    nb_non_mappes = df[df["code_insee_2024"].isna()][col_geo_source].nunique()
    print(f"\n Codes sources non retrouvés dans notre référentiel : {nb_non_mappes}")

    print("\n HEAD (Aperçu) :")
    print(df_pivot.head(3))

if __name__ == "__main__":
    clean_criminalite_all(2024)