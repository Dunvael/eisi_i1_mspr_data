from pathlib import Path
import pandas as pd

#CSV de 2Go à transformer en parquet

FILE_DATA = Path("data_raw/2022_raw/Resultat_1er_tour_2022/RESULTAT_PAR_CANDIDATS_2022.csv")
OUTPUT = Path("data_cleaned/2022/presidentielle_2022_t1.parquet")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

usecols = [
    "id_election",
    "code_departement",
    "code_commune",
    "code_bv",
    "nom",
    "prenom",
    "voix",
    "ratio_voix_exprimes",
    "nuance"
]

chunks = []

for chunk in pd.read_csv(
    FILE_DATA,
    sep=";",
    usecols=usecols,
    chunksize=500000,
    engine="python",
    on_bad_lines="skip"
):
    filtered = chunk[chunk["id_election"] == "2022_pres_t1"]

    if not filtered.empty:
        chunks.append(filtered)
        print("Chunk trouvé :", filtered.shape)

df_final = pd.concat(chunks, ignore_index=True)

print(df_final.head())
print(df_final.shape)

df_final.to_parquet(OUTPUT, index=False)

print("Parquet créé :", OUTPUT)