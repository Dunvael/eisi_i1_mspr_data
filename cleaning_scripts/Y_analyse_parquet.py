import pandas as pd

df = pd.read_parquet(
    "data_raw/2022_raw/12. Resultat1er_tour/presidentielle_2022_t1.parquet"
)

resultat = df[
    df["code_commune"] == "balacet"
]

print(resultat.head())

#print(df.head(20))
#print(df.sample(10))