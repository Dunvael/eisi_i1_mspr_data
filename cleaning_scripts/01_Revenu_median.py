import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "10. 2021 Revenu pauvrete niveau vie" / "FILO2021_DISP_COM.csv"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def clean_revenus(year):
    print(f"Nettoyage revenus {year}")

    if not FILE_DATA.exists():
        print(f"Fichier revenu introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f"Référentiel communes introuvable : {FILE_COMMUNES}")
        print("Lancer d'abord : py scripts_v2/00_create_referentiel.py")
        sys.exit(1)

    # Référentiel communes
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str, encoding="utf-8")
    df_ref = df_ref[["code_insee", "nom_commune"]]
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # Lecture du fichier revenu brut
    try:
        df_raw = pd.read_csv(
            FILE_DATA,
            sep=";",
            dtype=str,
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        df_raw = pd.read_csv(
            FILE_DATA,
            sep=";",
            dtype=str,
            encoding="latin1"
        )

    # Nettoyer les noms de colonnes
    df_raw.columns = (
        df_raw.columns
        .astype(str)
        .str.strip()
        .str.replace('"', "", regex=False)
        .str.replace("'", "", regex=False)
    )

    print("Colonnes détectées :", df_raw.columns.tolist())

    # Colonnes utiles
    colonnes_a_garder = {
        "CODGEO": "code_insee",
        "Q221": "revenu_median"
    }

    if "CODGEO" not in df_raw.columns or "Q221" not in df_raw.columns:
        print("Colonnes nécessaires introuvables.")
        print("Colonnes disponibles :", list(df_raw.columns))
        sys.exit(1)

    df = df_raw[list(colonnes_a_garder.keys())].rename(columns=colonnes_a_garder)

    # Nettoyer code INSEE
    df["code_insee"] = df["code_insee"].astype(str).str.strip().str.zfill(5)

    # Convertir revenu médian en numérique
    # Les valeurs comme "s" deviennent NaN : c'est normal
    df["revenu_median"] = (
        df["revenu_median"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", "", regex=True)
        .str.replace(",", ".", regex=False)
    )

    df["revenu_median"] = pd.to_numeric(df["revenu_median"], errors="coerce")

    print("\n--- CONTRÔLE AVANT JOINTURE ---")
    print("Lignes brutes :", len(df_raw))
    print("Codes communes uniques :", df["code_insee"].nunique())
    print("NaN revenu :", df["revenu_median"].isna().sum())
    print("Pourcentage NaN revenu :", round(df["revenu_median"].isna().mean() * 100, 2), "%")
    print(df["revenu_median"].describe())

    print("Doublons dans df_ref :", df_ref["code_insee"].duplicated().sum())

    # Jointure avec référentiel communes
    df = pd.merge(df, df_ref, on="code_insee", how="left")

    print("\n--- CONTRÔLE JOINTURE ---")
    print("Lignes après jointure :", len(df))
    print("Communes non trouvées :", df["nom_commune"].isna().sum())

    # Supprimer uniquement les communes non trouvées
    df = df.dropna(subset=["nom_commune"])

    # Supprimer les doublons éventuels
    df = df.drop_duplicates(subset=["code_insee"])

    # Renommer
    df = df.rename(columns={"nom_commune": "localisation"})

    # 🚨 LA MAGIE : Au lieu de supprimer les doublons au hasard, on fait la moyenne des quartiers !
    df = df.groupby(['code_insee', 'localisation'], as_index=False)['revenu_median'].mean()

    # 🚨 Colonnes finales : ON GARDE ABSOLUMENT LE CODE INSEE
    df_final = df[["code_insee", "localisation", "revenu_median"]].copy()
    
    df_final["annee"] = year
    df_final["revenu_median"] = df_final["revenu_median"].round(0) # Arrondi propre

    print("\n--- CONTRÔLE FINAL ---")
    print("Lignes finales :", len(df_final))
    print("NaN revenu final :", df_final["revenu_median"].isna().sum())
    print("Pourcentage NaN final :", round(df_final["revenu_median"].isna().mean() * 100, 2), "%")
    print(df_final.head())

    fichier_sortie = DIR_OUTPUT / f"01_revenus_median_{year}_cleaned.csv"
    df_final.to_csv(fichier_sortie, sep=";", index=False, encoding="utf-8-sig")

    print(f"\n✅ Terminé : {len(df_final)} lignes sauvegardées avec leur Code INSEE !")
    print(f"Fichier créé : {fichier_sortie}")

if __name__ == "__main__":
    clean_revenus(2021)