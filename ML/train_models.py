import sqlite3
import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.utils.class_weight import compute_sample_weight # AJOUT : Pour équilibrer XGBoost

from xgboost import XGBClassifier


# 0. Configuration générale

DB_PATH = "data_cleaned/Train_dataframe.db"

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

BEST_MODEL_PATH = MODEL_DIR / "best_model.joblib"
ENCODER_PATH = MODEL_DIR / "label_encoder.joblib"
FEATURES_PATH = MODEL_DIR / "features.joblib" # AJOUT : Chemin pour sauver les colonnes

ARTIFACTS_DIR = Path("artifacts")
CLASSIFICATION_DIR = ARTIFACTS_DIR / "classification"

REPORTS_DIR = CLASSIFICATION_DIR / "reports"
PREDICTIONS_DIR = CLASSIFICATION_DIR / "predictions"
IMPORTANCES_DIR = CLASSIFICATION_DIR / "importances"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
IMPORTANCES_DIR.mkdir(parents=True, exist_ok=True)

TARGET_COLUMN = "classe_politique"
RANDOM_STATE = 42


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

y = df[TARGET_COLUMN]

encoder = LabelEncoder()
y = encoder.fit_transform(y)

print("\nClasses politiques :")
print(encoder.classes_)


# 3. Définition des variables explicatives

X = df.drop(columns=[
    "classe_politique",
    "localisation",
    "code_insee",
    "annee"
], errors="ignore")

X = pd.get_dummies(X, drop_first=False)

# AJOUT CRITIQUE : Sauvegarde de la liste exacte des colonnes pour 2024
joblib.dump(list(X.columns), FEATURES_PATH)
print(f"\nVariables sauvegardées pour la prédiction : {len(X.columns)}")


# 4. Vérification des valeurs manquantes

print("\nNaN dans les variables explicatives :")
print(X.isna().sum())

print("\nPourcentage de NaN par colonne :")
print((X.isna().mean() * 100).round(2))


# 5. Séparation entraînement / test

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=RANDOM_STATE,
    stratify=y
)

print("\nTrain :", X_train.shape)
print("Test :", X_test.shape)


# 6. Définition des modèles à entraîner

models = {
    "Random Forest": Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=100,
            random_state=RANDOM_STATE,
            class_weight="balanced"
        ))
    ]),

    "XGBoost": Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("model", XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=RANDOM_STATE,
            eval_metric="mlogloss"
        ))
    ]),

    "Logistic Regression": Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=2000,
            random_state=RANDOM_STATE,
            class_weight="balanced"
        ))
    ]),

    "Neural Network": Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            solver="adam",
            max_iter=1000,
            random_state=RANDOM_STATE
        ))
    ])
}


# 7. Entraînement, prédiction et évaluation

results = []
best_model = None
best_model_name = None
best_model_file_name = None
best_f1_score = 0

for model_name, pipeline in models.items():
    print("\n" + "=" * 70)
    print("Modèle entraîné :", model_name)
    print("=" * 70)

    model_file_name = model_name.replace(" ", "_")

    # AJOUT CRITIQUE : Équilibrage des classes pour XGBoost
    if model_name == "XGBoost":
        weights = compute_sample_weight(class_weight='balanced', y=y_train)
        pipeline.fit(X_train, y_train, model__sample_weight=weights)
    else:
        pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    predictions_df = pd.DataFrame({
        "y_true": encoder.inverse_transform(y_test),
        "y_pred": encoder.inverse_transform(predictions)
    })

    predictions_df.to_csv(
        PREDICTIONS_DIR / f"predictions_{model_file_name}.csv",
        index=False
    )

    accuracy = accuracy_score(y_test, predictions)
    # AJOUT CRITIQUE : Utilisation de macro au lieu de weighted pour ne pas tricher
    f1_macro = f1_score(y_test, predictions, average="macro")

    print("\nAccuracy :", round(accuracy * 100, 2), "%")
    print("F1-score macro :", round(f1_macro * 100, 2), "%")

    print("\nRapport de classification :")
    print(classification_report(
        y_test,
        predictions,
        target_names=encoder.classes_,
        zero_division=0
    ))

    results.append({
        "modele": model_name,
        "model_file_name": model_file_name,
        "accuracy": round(accuracy, 4),
        "f1_macro": round(f1_macro, 4)
    })

    if f1_macro > best_f1_score:
        best_f1_score = f1_macro
        best_model = pipeline
        best_model_name = model_name
        best_model_file_name = model_file_name

    model = pipeline.named_steps["model"]

    if hasattr(model, "feature_importances_"):
        importance = pd.DataFrame({
            "variable": X.columns,
            "importance": model.feature_importances_
        })

        importance = importance.sort_values(
            by="importance",
            ascending=False
        )

        importance.to_csv(
            IMPORTANCES_DIR / f"importance_{model_file_name}.csv",
            index=False
        )

        print("\nImportance des variables :")
        print(importance.head(50))

    elif hasattr(model, "coef_"):
        importance = pd.DataFrame({
            "variable": X.columns,
            "importance": abs(model.coef_).mean(axis=0)
        })

        importance = importance.sort_values(
            by="importance",
            ascending=False
        )

        importance.to_csv(
            IMPORTANCES_DIR / f"importance_{model_file_name}.csv",
            index=False
        )

        print("\nImportance approximative des variables :")
        print(importance.head(50))

    else:
        print("\nImportance des variables non disponible pour ce modèle.")


# 8. Comparaison finale des modèles

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="f1_macro",
    ascending=False
)

results_df.to_csv(
    REPORTS_DIR / "leaderboard_classification.csv",
    index=False
)

print("\n" + "=" * 70)
print("Comparaison finale des modèles")
print("=" * 70)

print(results_df)


# 9. Sauvegarde du meilleur modèle

joblib.dump(best_model, BEST_MODEL_PATH)
joblib.dump(encoder, ENCODER_PATH)

best_summary = {
    "modele": best_model_name,
    "model_file_name": best_model_file_name,
    "f1_macro": round(best_f1_score, 4)
}

with open(REPORTS_DIR / "best_model_classification_summary.json", "w", encoding="utf-8") as f:
    json.dump(best_summary, f, indent=4, ensure_ascii=False)

print("\nMeilleur modèle sélectionné :", best_model_name)
print("F1-score macro :", round(best_f1_score * 100, 2), "%")
print("Modèle sauvegardé dans :", BEST_MODEL_PATH)
print("Encoder sauvegardé dans :", ENCODER_PATH)
print("Exports dashboard créés dans :", CLASSIFICATION_DIR)