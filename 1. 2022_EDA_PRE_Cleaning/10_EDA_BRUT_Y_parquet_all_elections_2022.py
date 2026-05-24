import pandas as pd

df = pd.read_parquet(
    "data_raw/2022_raw/Resultat_1er_tour_2022/PRESIDENTIEL_T1_PAR_COM_2022.parquet"
)

resultat = df[
    df["code_commune"] == "balacet"
]

print(resultat.head())

print(df.shape)
print(df.head())
print(df.columns)
print(df.dtypes)

print(df["id_election"].value_counts())
print(df["code_commune"].isna().sum())
print(df["nom"].value_counts())
print(df["voix"].isna().sum())
print(df["nuance"].value_counts())

print(df.duplicated().sum())