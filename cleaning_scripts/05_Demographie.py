import pandas as pd
import numpy as np
from pathlib import Path
import sys

BASE_DIR = Path(".")

FILE_DATA = BASE_DIR / "data_raw" / "2022_raw" / "13. Demographie" / "pop-sexe-age-quinquennal6822.xlsx"
FILE_COMMUNES = BASE_DIR / "data_cleaned" / "communes_2022_cleaned.csv"

DIR_OUTPUT = BASE_DIR / "data_cleaned" / "2022"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)


def calcul_age_median(row, age_cols, midpoints): #row = une ligne = une commune
    total = row[age_cols].sum() #somme de toutes les tranches d’âge

    if total == 0: #si aucune population → pas d’âge médian
        return np.nan

    seuil = total / 2 #on cherche le moment où on atteint 50% de la population
    cumul = 0 #on va additionner les tranches petit à petit

    for col, midpoint in zip(age_cols, midpoints): #zip permet de parcourir 2 listes en mm temps
        cumul += row[col] # on ajoute la population tranche par tranche
        if cumul >= seuil: # dès qu'on dépasse 50% → c'est la tranche médiane
            return midpoint

    return np.nan


def clean_demographie(year):
    print(f"Nettoyage démographie {year}")

    if not FILE_DATA.exists():
        print(f" Fichier introuvable : {FILE_DATA}")
        sys.exit(1)

    if not FILE_COMMUNES.exists():
        print(f"  Référentiel introuvable : {FILE_COMMUNES}")
        sys.exit(1)

    # Référentiel communes
    df_ref = pd.read_csv(FILE_COMMUNES, sep=";", dtype=str)
    df_ref["code_insee"] = df_ref["code_insee"].astype(str).str.zfill(5)

    # Lecture de la feuille avec la ligne technique : DR, CR ..
    df = pd.read_excel(
        FILE_DATA,
        sheet_name="COM_2022",
        skiprows=13,
        dtype=str
    )

    df.columns = df.columns.astype(str).str.strip()

    # Code INSEE = département + code commune
    df["DR"] = df["DR"].astype(str).str.zfill(2)
    df["CR"] = df["CR"].astype(str).str.zfill(3)
    df["code_insee"] = df["DR"] + df["CR"]

    df = df[df["STABLE"].astype(str).str.strip() == "1"] #On garde uniquement les communes STABLES (communes non fusionnées non supprimée)


    # Colonnes source → colonnes propres
    tranches = {
        "0_4": ("ageq_rec01s1rpop2022", "ageq_rec01s2rpop2022", 2.5),
        "5_9": ("ageq_rec02s1rpop2022", "ageq_rec02s2rpop2022", 7.5),
        "10_14": ("ageq_rec03s1rpop2022", "ageq_rec03s2rpop2022", 12.5),
        "15_19": ("ageq_rec04s1rpop2022", "ageq_rec04s2rpop2022", 17.5),
        "20_24": ("ageq_rec05s1rpop2022", "ageq_rec05s2rpop2022", 22.5),
        "25_29": ("ageq_rec06s1rpop2022", "ageq_rec06s2rpop2022", 27.5),
        "30_34": ("ageq_rec07s1rpop2022", "ageq_rec07s2rpop2022", 32.5),
        "35_39": ("ageq_rec08s1rpop2022", "ageq_rec08s2rpop2022", 37.5),
        "40_44": ("ageq_rec09s1rpop2022", "ageq_rec09s2rpop2022", 42.5),
        "45_49": ("ageq_rec10s1rpop2022", "ageq_rec10s2rpop2022", 47.5),
        "50_54": ("ageq_rec11s1rpop2022", "ageq_rec11s2rpop2022", 52.5),
        "55_59": ("ageq_rec12s1rpop2022", "ageq_rec12s2rpop2022", 57.5),
        "60_64": ("ageq_rec13s1rpop2022", "ageq_rec13s2rpop2022", 62.5),
        "65_69": ("ageq_rec14s1rpop2022", "ageq_rec14s2rpop2022", 67.5),
        "70_74": ("ageq_rec15s1rpop2022", "ageq_rec15s2rpop2022", 72.5),
        "75_79": ("ageq_rec16s1rpop2022", "ageq_rec16s2rpop2022", 77.5),
        "80_84": ("ageq_rec17s1rpop2022", "ageq_rec17s2rpop2022", 82.5),
        "85_89": ("ageq_rec18s1rpop2022", "ageq_rec18s2rpop2022", 87.5),
        "90_94": ("ageq_rec19s1rpop2022", "ageq_rec19s2rpop2022", 92.5),
        "95_plus": ("ageq_rec20s1rpop2022", "ageq_rec20s2rpop2022", 97.5),
    }

    age_cols = []
    midpoints = []

    for tranche, (col_hommes, col_femmes, milieu) in tranches.items():
        if col_hommes not in df.columns or col_femmes not in df.columns:
            print(f"  Colonnes manquantes pour {tranche}")
            print(f"Attendu : {col_hommes} et {col_femmes}")
            print("Colonnes disponibles :", df.columns.tolist())
            sys.exit(1)

        hommes = pd.to_numeric(df[col_hommes], errors="coerce").fillna(0)
        femmes = pd.to_numeric(df[col_femmes], errors="coerce").fillna(0)

        df[tranche] = hommes + femmes

        age_cols.append(tranche)
        midpoints.append(milieu)

    # Groupes démographiques
    df["population_totale"] = df[age_cols].sum(axis=1)

    df["jeunes_moins_25"] = df[
        ["0_4", "5_9", "10_14", "15_19", "20_24"]
    ].sum(axis=1)

    df["seniors_65_plus"] = df[
        ["65_69", "70_74", "75_79", "80_84", "85_89", "90_94", "95_plus"]
    ].sum(axis=1)

    df["pct_jeunes"] = np.where(
        df["population_totale"] > 0,
        df["jeunes_moins_25"] / df["population_totale"] * 100,
        np.nan
    )

    df["pct_seniors"] = np.where(
        df["population_totale"] > 0,
        df["seniors_65_plus"] / df["population_totale"] * 100,
        np.nan
    )

    # Age médian approximatif : tranche où le cumul dépasse 50%
    df["age_median"] = df.apply(
        lambda row: calcul_age_median(row, age_cols, midpoints),
        axis=1
    )

    # Jointure avec le référentiel
    df = pd.merge(df, df_ref, on="code_insee", how="left")
    df = df.rename(columns={"nom_commune": "localisation"})

    df_final = df[
        [
            "localisation",
            "pct_jeunes",
            "pct_seniors",
            "age_median",
        ]
    ].copy()


    #supprimer les lignes vides
    df_final = df_final.dropna(subset=["localisation", "pct_jeunes", "pct_seniors", "age_median"]) #Suppression lignes où les variables essentielles sont manquantes
    df_final = df_final[df_final["localisation"].astype(str).str.strip() != ""]

    df_final["annee"] = year #ajout de l'année

    #arrondir
    cols_num = ["pct_jeunes", "pct_seniors", "age_median"]
    df_final[cols_num] = df_final[cols_num].round(2)

    #Export
    fichier = DIR_OUTPUT / f"05_demographie_{year}_cleaned.csv"
    df_final.to_csv(fichier, sep=";", index=False, encoding="utf-8-sig")

    print(f" Fichier créé : {fichier}")
    print(f" Lignes sauvegardées : {len(df_final)}")

    #DEBUG : 
    #df_null = df_final[
    #df_final["pct_jeunes"].isna() |
    #df_final["pct_seniors"].isna() |
    #df_final["age_median"].isna()]

if __name__ == "__main__":
    clean_demographie(2022)