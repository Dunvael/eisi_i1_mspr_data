from __future__ import annotations

"""
Pipeline de régression pour le projet MSPR / Electio-Analytics.

Objectif
--------
Comparer plusieurs modèles de régression supervisée afin de prédire
une valeur numérique liée aux résultats électoraux.

Exemples de cibles possibles :
- score_extreme_droite
- score_centre
- score_gauche
- score_droite
- taux_abstention

Ce script :
- charge un CSV final
- vérifie les colonnes attendues
- détecte les variables numériques et catégorielles
- applique un prétraitement automatique
- compare plusieurs modèles de régression
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
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR

warnings.filterwarnings("ignore")

RANDOM_STATE = 42


@dataclass
class RegressionConfig:
    """Configuration centrale du pipeline de régression."""

    csv_path: str = "data/final_dataset.csv"
    target_column: str = "score_extreme_droite"
    test_size: float = 0.2
    id_columns: list[str] = field(default_factory=lambda: ["annee", "code_commune", "nom_commune"])
    drop_columns: list[str] = field(default_factory=list)
    numeric_features: Optional[list[str]] = None
    categorical_features: Optional[list[str]] = None
    model_dir: str = "artifacts/regression/models"
    report_dir: str = "artifacts/regression/reports"
    predictions_dir: str = "artifacts/regression/predictions"
    cv_folds: int = 5
    sort_leaderboard_by: str = "rmse_test"


CONFIG = RegressionConfig(
    csv_path="data/final_dataset.csv",
    target_column="score_extreme_droite",
    test_size=0.2,
    id_columns=["annee", "code_commune", "nom_commune"],
    drop_columns=[],
    numeric_features=None,
    categorical_features=None,
    cv_folds=5,
    sort_leaderboard_by="rmse_test",
)


def ensure_directories(cfg: RegressionConfig) -> None:
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



def validate_config_columns(df: pd.DataFrame, cfg: RegressionConfig) -> None:
    """Vérifie la présence des colonnes indispensables dans le dataframe."""
    missing = []
    required = [cfg.target_column] + cfg.id_columns + cfg.drop_columns

    for col in required:
        if col and col not in df.columns:
            missing.append(col)

    if missing:
        raise ValueError(f"Colonnes absentes du dataset : {missing}")



def infer_feature_types(df: pd.DataFrame, cfg: RegressionConfig) -> tuple[list[str], list[str]]:
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
    """Définit les modèles de régression à comparer."""
    return {
        "ridge": Ridge(alpha=1.0),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators=300,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "extra_trees_regressor": ExtraTreesRegressor(
            n_estimators=300,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "svr_rbf": SVR(kernel="rbf", C=1.0, epsilon=0.1),
    }



def build_scoring() -> dict[str, str]:
    """Définit les métriques utilisées pendant la validation croisée."""
    return {
        "r2": "r2",
        "neg_mae": "neg_mean_absolute_error",
        "neg_rmse": "neg_root_mean_squared_error",
    }



def split_data(
    df: pd.DataFrame,
    cfg: RegressionConfig,
    numeric_features: list[str],
    categorical_features: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.DataFrame]:
    """Sépare les données en train/test."""
    feature_columns = numeric_features + categorical_features
    X = df[feature_columns].copy()
    y = df[cfg.target_column].copy()
    metadata = df[[c for c in cfg.id_columns if c in df.columns]].copy()

    X_train, X_test, y_train, y_test, _, meta_test = train_test_split(
        X,
        y,
        metadata,
        test_size=cfg.test_size,
        random_state=RANDOM_STATE,
    )

    return X_train, X_test, y_train, y_test, meta_test



def get_cv(cfg: RegressionConfig) -> KFold:
    """Retourne la stratégie de validation croisée pour la régression."""
    return KFold(n_splits=cfg.cv_folds, shuffle=True, random_state=RANDOM_STATE)



def evaluate_regression(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, Any]:
    """Calcule les métriques de test pour la régression."""
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "r2_test": float(r2_score(y_true, y_pred)),
        "mae_test": float(mean_absolute_error(y_true, y_pred)),
        "rmse_test": rmse,
    }



def train_and_compare_models(
    df: pd.DataFrame,
    cfg: RegressionConfig,
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

        row: dict[str, Any] = {"model": model_name}
        row["cv_r2_mean"] = float(np.mean(cv_scores["test_r2"]))
        row["cv_r2_std"] = float(np.std(cv_scores["test_r2"]))
        row["cv_mae_mean"] = float(-np.mean(cv_scores["test_neg_mae"]))
        row["cv_mae_std"] = float(np.std(-cv_scores["test_neg_mae"]))
        row["cv_rmse_mean"] = float(-np.mean(cv_scores["test_neg_rmse"]))
        row["cv_rmse_std"] = float(np.std(-cv_scores["test_neg_rmse"]))

        row.update(evaluate_regression(y_test, y_pred))
        leaderboard_rows.append(row)

        pred_df = meta_test.copy()
        pred_df["y_true"] = y_test.values
        pred_df["y_pred"] = y_pred

        pred_path = Path(cfg.predictions_dir) / f"predictions_{model_name}.csv"
        pred_df.to_csv(pred_path, index=False)

    leaderboard = pd.DataFrame(leaderboard_rows)
    leaderboard = leaderboard.sort_values(
        by=cfg.sort_leaderboard_by,
        ascending=True,
    ).reset_index(drop=True)

    best_model_name = leaderboard.iloc[0]["model"]
    best_model = fitted_models[best_model_name]
    joblib.dump(best_model, Path(cfg.model_dir) / "best_model_regression.joblib")

    best_row = leaderboard.iloc[0].to_dict()
    with open(Path(cfg.report_dir) / "best_model_regression_summary.json", "w", encoding="utf-8") as f:
        json.dump(best_row, f, ensure_ascii=False, indent=2)

    leaderboard.to_csv(Path(cfg.report_dir) / "leaderboard_regression.csv", index=False)

    return leaderboard, best_row



def main() -> None:
    """Point d'entrée du script."""
    ensure_directories(CONFIG)
    df = load_dataset(CONFIG.csv_path)
    leaderboard, best_row = train_and_compare_models(df, CONFIG)

    print("\n=== LEADERBOARD RÉGRESSION ===")
    print(leaderboard.to_string(index=False))

    print("\n=== MEILLEUR MODÈLE DE RÉGRESSION ===")
    print(json.dumps(best_row, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
