import pandas as pd


# CONFIGURATION

FILE_RAW = "data_raw/2022_raw/5_demographie_2022/DEMOGRAPHIE_PAR_SEXE_PAR_DEP_ET_COM_1968_TO_2022.xlsx"


# LECTURE DU DATASET BRUT

df = pd.read_excel(
    FILE_RAW,
    sheet_name="COM_2022",
    skiprows=13,
    dtype=str
)

df.columns = df.columns.astype(str).str.strip()


# INFOS GÉNÉRALES

print("\n--- DIMENSIONS DU DATASET ---")
print(df.shape)

print("\n--- APERÇU DES DONNÉES ---")
print(df.head())

print("\n--- NOMS DES COLONNES ---")
print(df.columns)


# ANALYSE DES DOUBLONS

print("\n--- DOUBLONS ---")
print(df.duplicated().sum())


# ANALYSE DES CODES INSEE

if "DR" in df.columns and "CR" in df.columns:

    df["code_insee"] = (
        df["DR"].astype(str).str.zfill(2)
        + df["CR"].astype(str).str.zfill(3)
    )

    print("\n--- NOMBRE DE CODES INSEE UNIQUES ---")
    print(df["code_insee"].nunique())

    print("\n--- LONGUEUR DES CODES INSEE ---")
    print(df["code_insee"].astype(str).str.len().value_counts())

    print("\n--- DOUBLONS SUR CODE INSEE ---")
    print(df.duplicated(subset=["code_insee"]).sum())


# ANALYSE DES COLONNES NUMÉRIQUES

colonnes_numeriques = [
    "ageq_rec01s1rpop2022",
    "ageq_rec01s2rpop2022",
    "ageq_rec02s1rpop2022",
    "ageq_rec02s2rpop2022",
    "ageq_rec03s1rpop2022",
    "ageq_rec03s2rpop2022",
    "ageq_rec04s1rpop2022",
    "ageq_rec04s2rpop2022",
    "ageq_rec05s1rpop2022",
    "ageq_rec05s2rpop2022",
    "ageq_rec06s1rpop2022",
    "ageq_rec06s2rpop2022",
    "ageq_rec07s1rpop2022",
    "ageq_rec07s2rpop2022",
    "ageq_rec08s1rpop2022",
    "ageq_rec08s2rpop2022",
    "ageq_rec09s1rpop2022",
    "ageq_rec09s2rpop2022",
    "ageq_rec10s1rpop2022",
    "ageq_rec10s2rpop2022",
    "ageq_rec11s1rpop2022",
    "ageq_rec11s2rpop2022",
    "ageq_rec12s1rpop2022",
    "ageq_rec12s2rpop2022",
    "ageq_rec13s1rpop2022",
    "ageq_rec13s2rpop2022",
    "ageq_rec14s1rpop2022",
    "ageq_rec14s2rpop2022",
    "ageq_rec15s1rpop2022",
    "ageq_rec15s2rpop2022",
    "ageq_rec16s1rpop2022",
    "ageq_rec16s2rpop2022",
    "ageq_rec17s1rpop2022",
    "ageq_rec17s2rpop2022",
    "ageq_rec18s1rpop2022",
    "ageq_rec18s2rpop2022",
    "ageq_rec19s1rpop2022",
    "ageq_rec19s2rpop2022",
    "ageq_rec20s1rpop2022",
    "ageq_rec20s2rpop2022"
]

colonnes_presentes = [
    col for col in colonnes_numeriques
    if col in df.columns
]

print("\n--- COLONNES NUMÉRIQUES PRÉSENTES ---")
print(colonnes_presentes)