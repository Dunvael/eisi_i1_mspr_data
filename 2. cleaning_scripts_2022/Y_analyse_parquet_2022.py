import pandas as pd

df = pd.read_parquet(
    "data_raw/2022_raw/Resultat_1er_tour_2022/PRESIDENTIEL_T1_PAR_COM_2022.parquet"
)

resultat = df[
    df["code_commune"] == "balacet"
]

print(resultat.head())

#print(df.head(20))
#print(df.sample(10))