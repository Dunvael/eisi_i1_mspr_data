# import pandas as pd

# df = pd.read_csv("data_cleaned/2022/01_revenus_median_2021_cleaned.csv", sep=";")

# print(df.shape)
# print(df.info())
# print(df.describe())
# print(df.isna().sum())

import pandas as pd

file_path = "data_raw/2022_raw/10. 2021 Revenu pauvrete niveau vie/BASE_TD_FILO_IRIS_2021_DEC.xlsx"

df = pd.read_excel(file_path)

print(df.shape)
print(df.info())
print(df.head())