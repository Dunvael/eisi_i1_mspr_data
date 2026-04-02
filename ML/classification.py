from __future__ import annotations

"""
Pipeline de classification pour le projet MSPR / Electio-Analytics.

Objectif
--------
Comparer plusieurs modèles de classification supervisée afin de prédire
le bloc politique gagnant à partir d'indicateurs socio-économiques,
démographiques et électoraux.

Exemples de classes cibles :
- gauche
- centre
- droite
- extreme_droite
- extreme_gauche

Ce script :
- charge un CSV final
- vérifie les colonnes attendues
- détecte les variables numériques et catégorielles
- applique un prétraitement automatique
- compare plusieurs modèles de classification
- effectue une validation croisée
- évalue les performances sur un jeu de test
- exporte les prédictions, les métriques et le meilleur modèle
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import json
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

RANDOM_STATE = 42


@dataclass
class ClassificationConfig:
    """Configuration centrale du pipeline de classification."""

    csv_path: str = "data/final_dataset.csv"
    target_column: str = "bloc_politique"
    test_size: float = 0.2
    use_stratify: bool = True
    id_columns: list[str] = field(default_factory=lambda: ["annee", "code_commune", "nom_commune"])
    drop_columns: list[str] = field(default_factory=list)
    numeric_features: Optional[list[str]] = None
    categorical_features: Optional[list[str]] = None
    model_dir: str = "artifacts/classification/models"
    report_dir: str = "artifacts/classification/reports"
    predictions_dir: str = "artifacts/classification/predictions"
    cv_folds: int = 5
    sort_leaderboard_by: str = "f1_weighted_test"


CONFIG = ClassificationConfig(
    csv_path="data/final_dataset.csv",
    target_column="bloc_politique",
    test_size=0.2,
    use_stratify=True,
    id_columns=["annee", "code_commune", "nom_commune"],
    drop_columns=[],
    numeric_features=None,
    categorical_features=None,
    cv_folds=5,
    sort_leaderboard_by="f1_weighted_test",
)


def ensure_directories(cfg: ClassificationConfig) -> None:
    """Crée les dossiers de sortie si besoin."""
    Path(cfg.model_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.report_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.predictions_dir).mkdir(parents=True, exist_ok=True)



def load_dataset(csv_path: str) -> pd.DataFrame:
    """Charge le dataset CSV et vérifie qu'il n'est pas vide."""
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("Le dataset est vide.")
    return df



def validate_config_columns(df: pd.DataFrame, cfg: ClassificationConfig) -> None:
    """Vérifie la présence des colonnes indispensables dans le dataframe."""
    missing = []
    required = [cfg.target_column] + cfg.id_columns + cfg.drop_columns

    for col in required:
        if col and col not in df.columns:
            missing.append(col)

    if missing:
        raise ValueError(f"Colonnes absentes du dataset : {missing}")



def infer_feature_types(df: pd.DataFrame, cfg: ClassificationConfig) -> tuple[list[str], list[str]]:
    """
    Détecte automatiquement les variables numériques et catégorielles.

    On exclut la cible, les identifiants et les colonnes explicitement ignorées.
    """
    forbidden = set([cfg.target_column] + cfg.id_columns + cfg.drop_columns)
    candidate_columns = [c for c in df.columns if c not in forbidden]

    if cfg.numeric_features is None:
        numeric_features = df[candidate_columns].select_dtypes(include=[np.number]).columns.tolist()
    else:
        numeric_features = cfg.numeric_features

    if cfg.categorical_features is None:
        categorical_features = [c for c in candidate_columns if c not in numeric_features]
    else:
        categorical_features = cfg.categorical_features

    return numeric_features, categorical_features



def build_preprocessor(numeric_features: list[str], categorical_features: list[str]) -> ColumnTransformer:
    """
    Construit le bloc de prétraitement.

    Numérique : imputation médiane + standardisation.
    Catégoriel : imputation modalité fréquente + One-Hot Encoding.
    """
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )



def build_models() -> dict[str, Any]:
    """Définit les modèles de classification à comparer."""
    return {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "svm_rbf": SVC(
            probability=True,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
    }



def build_scoring() -> dict[str, str]:
    """Définit les métriques utilisées pendant la validation croisée."""
    return {
        "accuracy": "accuracy",
        "f1_weighted": "f1_weighted",
        "precision_weighted": "precision_weighted",
        "recall_weighted": "recall_weighted",
    }



def split_data(
    df: pd.DataFrame,
    cfg: ClassificationConfig,
    numeric_features: list[str],
    categorical_features: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.DataFrame]:
    """Sépare les données en train/test avec stratification si demandée."""
    feature_columns = numeric_features + categorical_features
    X = df[feature_columns].copy()
    y = df[cfg.target_column].copy()
    metadata = df[[c for c in cfg.id_columns if c in df.columns]].copy()

    stratify = y if cfg.use_stratify else None

    X_train, X_test, y_train, y_test, _, meta_test = train_test_split(
        X,
        y,
        metadata,
        test_size=cfg.test_size,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    return X_train, X_test, y_train, y_test, meta_test



def get_cv(cfg: ClassificationConfig) -> StratifiedKFold:
    """Retourne la stratégie de validation croisée pour la classification."""
    return StratifiedKFold(n_splits=cfg.cv_folds, shuffle=True, random_state=RANDOM_STATE)



def evaluate_classification(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, Any]:
    """Calcule les métriques de test pour la classification."""
    return {
        "accuracy_test": float(accuracy_score(y_true, y_pred)),
        "precision_weighted_test": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_weighted_test": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_weighted_test": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "classification_report": classification_report(
            y_true, y_pred, zero_division=0, output_dict=True
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }



def train_and_compare_models(
    df: pd.DataFrame,
    cfg: ClassificationConfig,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Fonction principale : entraîne, compare et sauvegarde les modèles."""
    validate_config_columns(df, cfg)
    numeric_features, categorical_features = infer_feature_types(df, cfg)

    if not numeric_features and not categorical_features:
        raise ValueError("Aucune feature exploitable n'a été détectée.")

    X_train, X_test, y_train, y_test, meta_test = split_data(
        df, cfg, numeric_features, categorical_features
    )
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    models = build_models()
    scoring = build_scoring()
    cv = get_cv(cfg)

    leaderboard_rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Pipeline] = {}

    for model_name, estimator in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", clone(preprocessor)),
                ("model", estimator),
            ]
        )

        cv_scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            return_train_score=False,
        )

        pipeline.fit(X_train, y_train)
        fitted_models[model_name] = pipeline

        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test) if hasattr(pipeline, "predict_proba") else None

        row: dict[str, Any] = {"model": model_name}
        for metric_name in scoring:
            row[f"cv_{metric_name}_mean"] = float(np.mean(cv_scores[f"test_{metric_name}"]))
            row[f"cv_{metric_name}_std"] = float(np.std(cv_scores[f"test_{metric_name}"]))

        row.update(evaluate_classification(y_test, y_pred))
        leaderboard_rows.append(row)

        pred_df = meta_test.copy()
        pred_df["y_true"] = y_test.values
        pred_df["y_pred"] = y_pred

        if y_proba is not None:
            model_classes = list(pipeline.named_steps["model"].classes_)
            for idx, class_name in enumerate(model_classes):
                pred_df[f"proba_{class_name}"] = y_proba[:, idx]

        pred_path = Path(cfg.predictions_dir) / f"predictions_{model_name}.csv"
        pred_df.to_csv(pred_path, index=False)

    leaderboard = pd.DataFrame(leaderboard_rows)
    leaderboard = leaderboard.sort_values(
        by=cfg.sort_leaderboard_by,
        ascending=False,
    ).reset_index(drop=True)

    best_model_name = leaderboard.iloc[0]["model"]
    best_model = fitted_models[best_model_name]
    joblib.dump(best_model, Path(cfg.model_dir) / "best_model_classification.joblib")

    best_row = leaderboard.iloc[0].to_dict()
    with open(Path(cfg.report_dir) / "best_model_classification_summary.json", "w", encoding="utf-8") as f:
        json.dump(best_row, f, ensure_ascii=False, indent=2)

    leaderboard.to_csv(Path(cfg.report_dir) / "leaderboard_classification.csv", index=False)

    return leaderboard, best_row



def main() -> None:
    """Point d'entrée du script."""
    ensure_directories(CONFIG)
    df = load_dataset(CONFIG.csv_path)
    leaderboard, best_row = train_and_compare_models(df, CONFIG)

    print("\n=== LEADERBOARD CLASSIFICATION ===")
    print(leaderboard.to_string(index=False))

    print("\n=== MEILLEUR MODÈLE DE CLASSIFICATION ===")
    print(json.dumps(best_row, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
