import pandas as pd
from pathlib import Path

BASE_DIR = Path(".")

FILE_DATA = (
    BASE_DIR / "data_raw" / "2022_raw" / "3. Criminalite" / "criminalite_par_commune.parquet"
)

FILE_PASSAGE = (
    BASE_DIR / "data_raw" / "2022_raw" / "referentiels" / "table_passage_annuelle_2025.xlsx"
)

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_criminalite_all(year):
    print(f"Nettoyage criminalité ALL {year}")

     # LECTURE CRIMINALITÉ
    df = pd.read_parquet(FILE_DATA)

    df["CODGEO_2025"] = (
        df["CODGEO_2025"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

     # LECTURE TABLE PASSAGE
     
    passage = pd.read_excel(FILE_PASSAGE, dtype=str, header=5)
    passage.columns = passage.columns.astype(str).str.strip()

    print(passage.columns.tolist())

    passage["CODGEO_2022"] = (
        passage["CODGEO_2022"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    passage["CODGEO_2025"] = (
        passage["CODGEO_2025"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    passage = passage[["CODGEO_2025", "CODGEO_2022"]].drop_duplicates()



     # MAPPING 2025 -> 2022

    df = df.merge(
        passage,
        on="CODGEO_2025",
        how="left"
    )

    df["code_insee"] = df["CODGEO_2022"].fillna(df["CODGEO_2025"])

    df["code_insee"] = (
        df["code_insee"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

     # CRIMES GARDÉS
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

     # FILTRE ANNÉE
    df = df[
        (df["annee"] == year) &
        (df["indicateur"].isin(indicateurs_gardes))
    ].copy()

     # TAUX FINAL
    df["taux_final"] = df["taux_pour_mille"].fillna(df["complement_info_taux"])

    df["taux_final"] = pd.to_numeric(
        df["taux_final"],
        errors="coerce"
    )

     # PIVOT
    df_pivot = df.pivot_table(
        index=["code_insee", "annee"],
        columns="indicateur",
        values="taux_final",
        aggfunc="mean"
    ).reset_index()

     # RENOMMAGE COLONNES
    df_pivot = df_pivot.rename(columns={
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

     # EXPORT
    fichier_sortie = DIR_OUTPUT / f"09_criminalite_diff_ndiff_{year}_cleaned.csv"

    df_pivot.to_csv(
        fichier_sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

     # DEBUG
    print(f"\nFichier créé : {fichier_sortie}")

    print("\nShape :")
    print(df_pivot.shape)

    print("\nHEAD :")
    print(df_pivot.head())

    print("\nNaN :")
    print(df_pivot.isna().sum())

    print("\nPourcentage NaN :")
    print((df_pivot.isna().mean() * 100).round(2))

    print("\nCodes 2025 non retrouvés dans la table de passage :")
    print(df[df["CODGEO_2022"].isna()]["CODGEO_2025"].nunique())


if __name__ == "__main__":
    clean_criminalite_all(2022)