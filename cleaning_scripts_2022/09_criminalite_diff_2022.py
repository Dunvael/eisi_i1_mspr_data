import pandas as pd
from pathlib import Path

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "09_criminalite_2022" / "CRIMINALITE_PAR_COM_2022.parquet"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_criminalite(year):
    print(f"Nettoyage criminalité {year}")

    df = pd.read_parquet(FILE_DATA)

    df = df.rename(columns={
        "CODGEO_2025": "code_insee"
    })

    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

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

    df = df[
        (df["annee"] == year) &
        (df["indicateur"].isin(indicateurs_gardes)) &
        (df["est_diffuse"] == "diff")
    ].copy()

    df["taux_pour_mille"] = pd.to_numeric(df["taux_pour_mille"], errors="coerce")
    df["taux_pour_mille"] = df["taux_pour_mille"].fillna(0)

    df_pivot = df.pivot_table(
        index=["code_insee", "annee"],
        columns="indicateur",
        values="taux_pour_mille",
        aggfunc="mean"
    ).reset_index()

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

    fichier_sortie = DIR_OUTPUT / f"09_criminalite_ONLY_diff_{year}_cleaned.csv"

    df_pivot.to_csv(
        fichier_sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Fichier créé : {fichier_sortie}")
    print("Shape :", df_pivot.shape)
    print(df_pivot.head())
    print(df_pivot.isna().sum())


if __name__ == "__main__":
    clean_criminalite(2022)