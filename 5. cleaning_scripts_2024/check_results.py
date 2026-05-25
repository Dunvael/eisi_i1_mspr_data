import pandas as pd


# STYLE TERMINAL

class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

print(f"\n{C.HEADER}{C.BOLD} LECTURE DES PRÉDICTIONS 2024{C.END}\n")


# Fichier contenant les prédictions politiques 2024 par commune
file_path = "data_cleaned/2024/PREDICTIONS_FINALES_2024.csv"

# Lecture du CSV (séparateur ;)
df = pd.read_csv(file_path, sep=";")


possible_cols = [
    "prediction_politique_2024",
    "prediction_politique",
    "prediction_encoded",
    "Parti_Politique_Texte"
]

colonne_cible = None
# On cherche la première colonne existante dans le DataFrame
for c in possible_cols:
    if c in df.columns:
        colonne_cible = c
        break

if colonne_cible is None:
    print(f"{C.WARNING}❌ Aucune colonne de prédiction trouvée !{C.END}")
    print("Colonnes disponibles :")
    print(df.columns.tolist())
    exit()


# 1. DISTRIBUTION

print(f"{C.OKBLUE}{C.BOLD}■ Répartition politique globale des communes :{C.END}")
# Comptage brut des catégories
repartition = df[colonne_cible].value_counts(dropna=False)
# Pourcentage de chaque catégorie
pourcentage = df[colonne_cible].value_counts(normalize=True, dropna=False) * 100
# Affichage propre en boucle
for trend in repartition.index:
    count = repartition[trend]
    pct = pourcentage[trend]
    print(f"  - {str(trend):<20} : {count:>7,} communes ({pct:.2f} %)")


# 2. SAMPLE

print(f"\n{C.OKBLUE}{C.BOLD}Échantillon des 15 premières communes :{C.END}")
print(f"{'-'*75}")
print(f"{'Code INSEE':<12} | {'Nom de la Commune':<30} | {'Prédiction 2024'}")
print(f"{'-'*75}")

for _, row in df.head(15).iterrows():
    code = str(row.get("code_insee_2024", "N/A"))
    nom = str(row.get("nom_commune_2024", "N/A"))
    valeur = str(row[colonne_cible])

    print(f"{code:<12} | {nom:<30} | {C.OKGREEN}{valeur}{C.END}")

print(f"{'-'*75}\n")