import pandas as pd

# Couleurs pour le terminal
class C:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

print(f"\n{C.HEADER}{C.BOLD}🧐 LECTURE DES PRÉDICTIONS GÉNÉRÉES POUR 2024{C.END}\n")

# Charger le fichier de résultats
file_path = "data_cleaned/2024/PREDICTIONS_FINALES_2024.csv"
df = pd.read_csv(file_path, sep=";")

# On cible la nouvelle colonne contenant le texte (ou les chiffres si le texte n'existe pas)
colonne_cible = "Parti_Politique_Texte" if "Parti_Politique_Texte" in df.columns else "prediction_politique_2024"

# 1. Distribution globale des prédictions
print(f"{C.OKBLUE}{C.BOLD}■ Répartition politique globale des communes :{C.END}")
repartition = df[colonne_cible].value_counts()
pourcentage = df[colonne_cible].value_counts(normalize=True) * 100

for trend, count in repartition.items():
    pct = pourcentage[trend]
    print(f"  - {str(trend):<18} : {count:>5,} communes ({pct:.2f} %)")

# 2. Aperçu de quelques communes
print(f"\n{C.OKBLUE}{C.BOLD}■ Échantillon des 15 premières communes :{C.END}")
print(f"{'-'*55}")
print(f"{'Code INSEE':<12} | {'Nom de la Commune':<20} | {'Prédiction 2024':<15}")
print(f"{'-'*55}")

for _, row in df.head(15).iterrows():
    valeur = str(row[colonne_cible])
    print(f"{str(row['code_insee_2024']).zfill(5):<12} | {str(row['nom_commune_2024']):<20} | {C.OKGREEN}{valeur}{C.END}")

print(f"{'-'*55}\n")