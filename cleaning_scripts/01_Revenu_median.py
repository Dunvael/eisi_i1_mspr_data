import pandas as pd
from pathlib import Path
import sys


BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "10. 2021 Revenu pauvrete niveau vie" / "FILO2021_DISP_COM.csv"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"
FILE_REVENU_DEP = BASE_DIR / "data_raw" / "2022_raw" / "10. 2021 Revenu pauvrete niveau vie" / "FILO2021_DEC_DEP.csv"
FILE_PASSAGE = BASE_DIR / "data_raw" / "2022_raw" / "referentiels" / "table_passage_annuelle_2025.xlsx"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.strip()
        .str.replace(r"\s+", "", regex=True)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    )


def clean_revenus(year):
    print(f"Nettoyage revenus {year}")

    for file_path in [FILE_DATA, FILE_COMMUNES, FILE_REVENU_DEP, FILE_PASSAGE]:
        if not file_path.exists():
            print(f"Fichier introuvable : {file_path}")
            sys.exit(1)

     # RÉFÉRENTIEL COMMUNES 2022
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str, encoding="utf-8")

    df_ref = df_ref[[
        "code_insee",
        "nom_commune",
        "code_departement",
        "code_region"
    ]].copy()

    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.strip().str.zfill(5)
    df_ref["code_departement"] = df_ref["code_departement"].astype(str).str.strip()
    df_ref["code_region"] = df_ref["code_region"].astype(str).str.strip()

    df_ref = df_ref.drop_duplicates(subset=["code_insee"])

     # TABLE PASSAGE 2021 -> 2022
    passage = pd.read_excel(FILE_PASSAGE, dtype=str, header=5)
    passage.columns = passage.columns.astype(str).str.strip()

    passage["CODGEO_2021"] = (
        passage["CODGEO_2021"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    passage["CODGEO_2022"] = (
        passage["CODGEO_2022"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    passage = passage[["CODGEO_2021", "CODGEO_2022"]].drop_duplicates()

     # LECTURE REVENUS COMMUNAUX 2021
    try:
        df_raw = pd.read_csv(FILE_DATA, sep=";", dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        df_raw = pd.read_csv(FILE_DATA, sep=";", dtype=str, encoding="latin1")

    df_raw.columns = (
        df_raw.columns.astype(str)
        .str.strip()
        .str.replace('"', "", regex=False)
        .str.replace("'", "", regex=False)
    )

    print("Colonnes fichier commune :", df_raw.columns.tolist())

    if "CODGEO" not in df_raw.columns or "Q221" not in df_raw.columns:
        print("Colonnes nécessaires introuvables dans fichier communal.")
        print("Colonnes disponibles :", list(df_raw.columns))
        sys.exit(1)

    df = df_raw[["CODGEO", "Q221"]].rename(columns={
        "CODGEO": "code_insee_2021",
        "Q221": "revenu_median_commune"
    })

    df["code_insee_2021"] = (
        df["code_insee_2021"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    df["revenu_median_commune"] = clean_numeric(df["revenu_median_commune"])

     # MAPPING 2021 -> 2022
    df = df.merge(
        passage,
        left_on="code_insee_2021",
        right_on="CODGEO_2021",
        how="left"
    )

    df["code_insee"] = df["CODGEO_2022"].fillna(df["code_insee_2021"])

    df["code_insee"] = (
        df["code_insee"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    print("\nCodes 2021 non retrouvés dans la table de passage :")
    print(df[df["CODGEO_2022"].isna()]["code_insee_2021"].nunique())

    # Dummy valeur manquante
    df["revenu_impute"] = df["revenu_median_commune"].isna().astype(int)

    print("\n--- CONTRÔLE AVANT JOINTURE ---")
    print("Lignes brutes :", len(df_raw))
    print("Codes communes 2021 uniques :", df["code_insee_2021"].nunique())
    print("Codes communes 2022 uniques :", df["code_insee"].nunique())
    print("NaN revenu communes :", df["revenu_median_commune"].isna().sum())
    print("Pourcentage NaN revenu communes :", round(df["revenu_median_commune"].isna().mean() * 100, 2), "%")

     # JOINTURE COMMUNES 2022
    df = pd.merge(df, df_ref, on="code_insee", how="left")

    print("\n--- CONTRÔLE JOINTURE COMMUNES 2022 ---")
    print("Lignes après jointure :", len(df))
    print("Communes non trouvées :", df["nom_commune"].isna().sum())

    df = df.dropna(subset=["nom_commune"])

     # LECTURE REVENU DÉPARTEMENT
    try:
        df_dep = pd.read_csv(FILE_REVENU_DEP, sep=";", dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        df_dep = pd.read_csv(FILE_REVENU_DEP, sep=";", dtype=str, encoding="latin1")

    df_dep.columns = (
        df_dep.columns.astype(str)
        .str.strip()
        .str.replace('"', "", regex=False)
        .str.replace("'", "", regex=False)
    )

    print("\nColonnes fichier département :", df_dep.columns.tolist())

    if "CODGEO" not in df_dep.columns or "Q221" not in df_dep.columns:
        print("Colonnes nécessaires introuvables dans le fichier département.")
        print("Colonnes disponibles :", list(df_dep.columns))
        sys.exit(1)

    df_dep = df_dep[["CODGEO", "Q221"]].rename(columns={
        "CODGEO": "code_departement",
        "Q221": "revenu_median_departement"
    })

    df_dep["code_departement"] = (
        df_dep["code_departement"]
        .astype(str)
        .str.strip()
        .str.zfill(2)
    )

    df_dep["revenu_median_departement"] = clean_numeric(
        df_dep["revenu_median_departement"]
    )

    df_dep = df_dep.drop_duplicates(subset=["code_departement"])

     # JOINTURE REVENU DÉPARTEMENT
    df = pd.merge(df, df_dep, on="code_departement", how="left")

    print("\n--- CONTRÔLE JOINTURE DÉPARTEMENT ---")
    print("Communes sans revenu département :", df["revenu_median_departement"].isna().sum())

     # IMPUTATION
    df["revenu_median_final"] = df["revenu_median_commune"].fillna(
        df["revenu_median_departement"]
    )

    print("\n--- CONTRÔLE IMPUTATION ---")
    print("NaN avant imputation :", df["revenu_median_commune"].isna().sum())
    print("NaN après imputation :", df["revenu_median_final"].isna().sum())
    print("Nbre revenus imputés :", df["revenu_impute"].sum())

     # FINAL
    df = df.rename(columns={"nom_commune": "localisation"})

    df_final = df[[
        "code_insee",
        "localisation",
        "code_departement",
        "code_region",
        "revenu_median_commune",
        "revenu_median_departement",
        "revenu_median_final",
        "revenu_impute"
    ]].copy()

    df_final["annee"] = year

    df_final["revenu_median_final"] = df_final["revenu_median_final"].round(2)
    df_final["revenu_median_commune"] = df_final["revenu_median_commune"].round(2)
    df_final["revenu_median_departement"] = df_final["revenu_median_departement"].round(2)

     # CLASSES REVENUS
    q1_revenu = df_final["revenu_median_final"].quantile(0.25)
    q3_revenu = df_final["revenu_median_final"].quantile(0.75)

    print("\n--- SEUILS CLASSES REVENUS ---")
    print("Q1 national communes :", round(q1_revenu, 2))
    print("Q3 national communes :", round(q3_revenu, 2))

    def classer_revenu(x):
        if pd.isna(x):
            return "inconnu"
        elif x < q1_revenu:
            return "pauvre"
        elif x > q3_revenu:
            return "riche"
        else:
            return "moyen"

    df_final["classe_revenu"] = df_final["revenu_median_final"].apply(classer_revenu)

    print("\n--- CONTRÔLE FINAL ---")
    print("Lignes finales :", len(df_final))
    print("NaN revenu final :", df_final["revenu_median_final"].isna().sum())
    print("Pourcentage NaN final :", round(df_final["revenu_median_final"].isna().mean() * 100, 2), "%")
    print(df_final.head(10))

    print("\n--- DISTRIBUTION CLASSES REVENUS ---")
    print(df_final["classe_revenu"].value_counts())

    fichier_sortie = DIR_OUTPUT / f"01_revenus_median_{year}_cleaned.csv"

    df_final.to_csv(
        fichier_sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nTerminé : {len(df_final)} lignes sauvegardées")
    print(f"Fichier créé : {fichier_sortie}")


if __name__ == "__main__":
    clean_revenus(2021)