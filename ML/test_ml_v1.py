import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report



df = pd.read_csv(
    "data_cleaned/2022/Z_dataframe_final_ml.csv",
    sep=";"
)

print(df.shape)
print(df.head())



# Ce qu'on veut prédire
y = df["classe_politique"]

# Transformer texte → nombre
encoder = LabelEncoder()

y = encoder.fit_transform(y)

print("\nClasses politiques :")
print(encoder.classes_)


X = df.drop(columns=[
    "classe_politique",
    "localisation",
    "code_insee",
    "score_extreme_droite",
    "score_extreme_gauche",
    "score_centre",
    "score_droite",
    "score_gauche",
    "annee"
])

# # Transformer classe_revenu en catégorie : pauvre/moyen/riche en colonnes numériques car randomforest comprends pas txt
# X = pd.get_dummies(
#     X,
#     columns=["classe_revenu"],
#     drop_first=False
# )

# Remplacer NaN par médiane : 
# X = X.fillna(X.median(numeric_only=True))

print("\nNaN après remplissage :")
print(X.isna().sum())



X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)

print("\nTrain :", X_train.shape)
print("Test :", X_test.shape)



model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print(classification_report(
    y_test,
    predictions,
    target_names=encoder.classes_
))

accuracy = accuracy_score(y_test, predictions)

print("\nAccuracy :", round(accuracy * 100, 2), "%")

importance = pd.DataFrame({
    "variable": X.columns,
    "importance": model.feature_importances_
})

print(
    importance.sort_values(
        by="importance",
        ascending=False
    )
)