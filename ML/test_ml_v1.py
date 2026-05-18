import pandas as pd
import sqlite3

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Chemin de la base SQLite
DB_PATH = "data_cleaned/Train_dataframe.db"


# 1. Chargement du dataframe depuis SQLite


conn = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    "SELECT * FROM training_data",
    conn
)

conn.close()

print("Dimensions du dataframe :", df.shape)
print(df.head())


# 2. Définition de la variable cible


# C'est la colonne que l'on cherche à prédire
y = df["classe_politique"]

# Transformation des classes textuelles en valeurs numériques
encoder = LabelEncoder()
y = encoder.fit_transform(y)

print("\nClasses politiques :")
print(encoder.classes_)


# 3. Définition des variables explicatives


X = df.drop(columns=[
    "classe_politique",
    "localisation",
    "code_insee",
    # "score_extreme_droite",
    # "score_extreme_gauche",
    # "score_centre",
    # "score_droite",
    # "score_gauche",
    "annee"
])

# # Transformer classe_revenu en catégorie : pauvre/moyen/riche en colonnes numériques car randomforest comprends pas txt
# X = pd.get_dummies(
#     X,
#     columns=["classe_revenu"],
#     drop_first=False
# )


# 4. Vérification des valeurs manquantes


print("\nNaN dans les variables explicatives :")
print(X.isna().sum())

# Si besoin, possibilité de remplacer les NaN par la médiane
# X = X.fillna(X.median(numeric_only=True))


# 5. Séparation entraînement / test


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)

print("\nTrain :", X_train.shape)
print("Test :", X_test.shape)


# 6. Entraînement du modèle


model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# 7. Évaluation du modèle


predictions = model.predict(X_test)

print("\nRapport de classification :")
print(classification_report(
    y_test,
    predictions,
    target_names=encoder.classes_
))

accuracy = accuracy_score(y_test, predictions)

print("\nAccuracy :", round(accuracy * 100, 2), "%")


# 8. Importance des variables


importance = pd.DataFrame({
    "variable": X.columns,
    "importance": model.feature_importances_
})

print("\nImportance des variables :")
print(
    importance.sort_values(
        by="importance",
        ascending=False
    )
)