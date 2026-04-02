from __future__ import annotations

"""
Tableau de bord Plotly pour comparer visuellement les modèles de classification
et de régression déjà entraînés.

Objectif
--------
Lire les exports générés par :
- classification.py
- regression.py

Puis afficher des graphiques interactifs pour la soutenance :
- comparaison des métriques des modèles
- matrice de confusion du meilleur modèle de classification
- comparaison réel vs prédit pour le meilleur modèle de régression
- possibilité de filtrer certaines vues par année si la colonne existe

Lancement
---------
python comparatif_visuel_modeles.py

Prérequis
---------
pip install pandas plotly dash

Exports attendus
----------------
Classification :
- artifacts/classification/reports/leaderboard_classification.csv
- artifacts/classification/reports/best_model_classification_summary.json
- artifacts/classification/predictions/predictions_<modele>.csv

Régression :
- artifacts/regression/reports/leaderboard_regression.csv
- artifacts/regression/reports/best_model_regression_summary.json
- artifacts/regression/predictions/predictions_<modele>.csv
"""

from pathlib import Path
import json
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html


# ==============================
# Configuration des chemins
# ==============================
BASE_DIR = Path("artifacts")

CLASSIFICATION_REPORTS_DIR = BASE_DIR / "classification" / "reports"
CLASSIFICATION_PREDICTIONS_DIR = BASE_DIR / "classification" / "predictions"

REGRESSION_REPORTS_DIR = BASE_DIR / "regression" / "reports"
REGRESSION_PREDICTIONS_DIR = BASE_DIR / "regression" / "predictions"

CLASSIFICATION_LEADERBOARD_PATH = CLASSIFICATION_REPORTS_DIR / "leaderboard_classification.csv"
CLASSIFICATION_BEST_SUMMARY_PATH = CLASSIFICATION_REPORTS_DIR / "best_model_classification_summary.json"

REGRESSION_LEADERBOARD_PATH = REGRESSION_REPORTS_DIR / "leaderboard_regression.csv"
REGRESSION_BEST_SUMMARY_PATH = REGRESSION_REPORTS_DIR / "best_model_regression_summary.json"


# ==============================
# Fonctions utilitaires
# ==============================
def safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    """Lit un CSV s'il existe, sinon retourne None."""
    if not path.exists():
        return None
    return pd.read_csv(path)



def safe_read_json(path: Path) -> Optional[dict]:
    """Lit un JSON s'il existe, sinon retourne None."""
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)



def load_classification_data() -> tuple[Optional[pd.DataFrame], Optional[dict], Optional[pd.DataFrame]]:
    """Charge les exports de classification."""
    leaderboard = safe_read_csv(CLASSIFICATION_LEADERBOARD_PATH)
    best_summary = safe_read_json(CLASSIFICATION_BEST_SUMMARY_PATH)

    predictions = None
    if best_summary is not None:
        model_name = best_summary.get("model")
        if model_name:
            pred_path = CLASSIFICATION_PREDICTIONS_DIR / f"predictions_{model_name}.csv"
            predictions = safe_read_csv(pred_path)

    return leaderboard, best_summary, predictions



def load_regression_data() -> tuple[Optional[pd.DataFrame], Optional[dict], Optional[pd.DataFrame]]:
    """Charge les exports de régression."""
    leaderboard = safe_read_csv(REGRESSION_LEADERBOARD_PATH)
    best_summary = safe_read_json(REGRESSION_BEST_SUMMARY_PATH)

    predictions = None
    if best_summary is not None:
        model_name = best_summary.get("model")
        if model_name:
            pred_path = REGRESSION_PREDICTIONS_DIR / f"predictions_{model_name}.csv"
            predictions = safe_read_csv(pred_path)

    return leaderboard, best_summary, predictions



def build_empty_figure(title: str) -> go.Figure:
    """Construit une figure vide avec un message explicite."""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": "Aucune donnée disponible. Lancez d'abord classification.py et/ou regression.py.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16},
            }
        ],
        height=450,
    )
    return fig



def build_classification_metric_chart(leaderboard: Optional[pd.DataFrame]) -> go.Figure:
    """Crée un graphique comparatif des métriques de classification."""
    if leaderboard is None or leaderboard.empty:
        return build_empty_figure("Comparatif des modèles de classification")

    metric_columns = [
        col for col in ["accuracy_test", "precision_weighted_test", "recall_weighted_test", "f1_weighted_test"]
        if col in leaderboard.columns
    ]

    if not metric_columns:
        return build_empty_figure("Comparatif des modèles de classification")

    plot_df = leaderboard[["model"] + metric_columns].melt(
        id_vars="model",
        value_vars=metric_columns,
        var_name="metric",
        value_name="score",
    )

    fig = px.bar(
        plot_df,
        x="model",
        y="score",
        color="metric",
        barmode="group",
        title="Comparatif des modèles de classification",
        text_auto=".3f",
    )
    fig.update_layout(height=500)
    return fig



def build_regression_metric_chart(leaderboard: Optional[pd.DataFrame]) -> go.Figure:
    """Crée un graphique comparatif des métriques de régression."""
    if leaderboard is None or leaderboard.empty:
        return build_empty_figure("Comparatif des modèles de régression")

    metric_columns = [
        col for col in ["r2_test", "mae_test", "rmse_test"]
        if col in leaderboard.columns
    ]

    if not metric_columns:
        return build_empty_figure("Comparatif des modèles de régression")

    plot_df = leaderboard[["model"] + metric_columns].melt(
        id_vars="model",
        value_vars=metric_columns,
        var_name="metric",
        value_name="score",
    )

    fig = px.bar(
        plot_df,
        x="model",
        y="score",
        color="metric",
        barmode="group",
        title="Comparatif des modèles de régression",
        text_auto=".3f",
    )
    fig.update_layout(height=500)
    return fig



def build_confusion_matrix_figure(predictions: Optional[pd.DataFrame]) -> go.Figure:
    """Construit une matrice de confusion à partir des prédictions du meilleur modèle de classification."""
    if predictions is None or predictions.empty or "y_true" not in predictions.columns or "y_pred" not in predictions.columns:
        return build_empty_figure("Matrice de confusion - Meilleur modèle de classification")

    labels = sorted(set(predictions["y_true"].astype(str)).union(set(predictions["y_pred"].astype(str))))
    matrix = pd.crosstab(
        predictions["y_true"].astype(str),
        predictions["y_pred"].astype(str),
        rownames=["Réel"],
        colnames=["Prédit"],
        dropna=False,
    )

    matrix = matrix.reindex(index=labels, columns=labels, fill_value=0)

    fig = px.imshow(
        matrix,
        text_auto=True,
        aspect="auto",
        title="Matrice de confusion - Meilleur modèle de classification",
    )
    fig.update_layout(height=550)
    return fig



def build_regression_scatter_figure(predictions: Optional[pd.DataFrame], selected_year: str) -> go.Figure:
    """Construit un nuage de points Réel vs Prédit pour la régression."""
    if predictions is None or predictions.empty or "y_true" not in predictions.columns or "y_pred" not in predictions.columns:
        return build_empty_figure("Réel vs Prédit - Meilleur modèle de régression")

    plot_df = predictions.copy()

    if selected_year != "Toutes" and "annee" in plot_df.columns:
        plot_df = plot_df[plot_df["annee"].astype(str) == str(selected_year)]

    if plot_df.empty:
        return build_empty_figure("Réel vs Prédit - Meilleur modèle de régression")

    fig = px.scatter(
        plot_df,
        x="y_true",
        y="y_pred",
        hover_data=[col for col in ["annee", "code_commune", "nom_commune"] if col in plot_df.columns],
        title="Réel vs Prédit - Meilleur modèle de régression",
    )

    min_val = min(plot_df["y_true"].min(), plot_df["y_pred"].min())
    max_val = max(plot_df["y_true"].max(), plot_df["y_pred"].max())

    fig.add_trace(
        go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            name="Prédiction parfaite",
        )
    )
    fig.update_layout(height=550)
    return fig



def build_regression_residuals_figure(predictions: Optional[pd.DataFrame], selected_year: str) -> go.Figure:
    """Construit un graphique des résidus pour la régression."""
    if predictions is None or predictions.empty or "y_true" not in predictions.columns or "y_pred" not in predictions.columns:
        return build_empty_figure("Résidus - Meilleur modèle de régression")

    plot_df = predictions.copy()

    if selected_year != "Toutes" and "annee" in plot_df.columns:
        plot_df = plot_df[plot_df["annee"].astype(str) == str(selected_year)]

    if plot_df.empty:
        return build_empty_figure("Résidus - Meilleur modèle de régression")

    plot_df["residu"] = plot_df["y_true"] - plot_df["y_pred"]

    fig = px.scatter(
        plot_df,
        x="y_pred",
        y="residu",
        hover_data=[col for col in ["annee", "code_commune", "nom_commune"] if col in plot_df.columns],
        title="Résidus - Meilleur modèle de régression",
    )
    fig.add_hline(y=0)
    fig.update_layout(height=550)
    return fig



def get_year_options(*dfs: Optional[pd.DataFrame]) -> list[dict[str, str]]:
    """Construit la liste des années disponibles dans les exports de prédiction."""
    years = set()
    for df in dfs:
        if df is not None and not df.empty and "annee" in df.columns:
            years.update(df["annee"].dropna().astype(str).unique().tolist())

    options = [{"label": "Toutes", "value": "Toutes"}]
    for year in sorted(years):
        options.append({"label": year, "value": year})
    return options


# ==============================
# Chargement initial des données
# ==============================
classification_leaderboard, classification_best_summary, classification_predictions = load_classification_data()
regression_leaderboard, regression_best_summary, regression_predictions = load_regression_data()

year_options = get_year_options(classification_predictions, regression_predictions)


# ==============================
# Application Dash
# ==============================
app = Dash(__name__)
app.title = "Comparatif visuel des modèles"

app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H1("Comparatif visuel des modèles de machine learning"),
        html.P(
            "Ce tableau de bord lit les exports générés automatiquement par classification.py et regression.py."
        ),

        html.Div(
            style={"marginBottom": "20px", "maxWidth": "300px"},
            children=[
                html.Label("Filtrer par année (si disponible)"),
                dcc.Dropdown(
                    id="year-filter",
                    options=year_options,
                    value="Toutes",
                    clearable=False,
                ),
            ],
        ),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
            children=[
                html.Div(
                    children=[
                        html.H2("Classification"),
                        html.P(
                            f"Meilleur modèle : {classification_best_summary.get('model', 'Non disponible') if classification_best_summary else 'Non disponible'}"
                        ),
                        dcc.Graph(
                            id="classification-metrics-chart",
                            figure=build_classification_metric_chart(classification_leaderboard),
                        ),
                        dcc.Graph(
                            id="classification-confusion-matrix",
                            figure=build_confusion_matrix_figure(classification_predictions),
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.H2("Régression"),
                        html.P(
                            f"Meilleur modèle : {regression_best_summary.get('model', 'Non disponible') if regression_best_summary else 'Non disponible'}"
                        ),
                        dcc.Graph(
                            id="regression-metrics-chart",
                            figure=build_regression_metric_chart(regression_leaderboard),
                        ),
                        dcc.Graph(id="regression-scatter"),
                        dcc.Graph(id="regression-residuals"),
                    ]
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("regression-scatter", "figure"),
    Output("regression-residuals", "figure"),
    Input("year-filter", "value"),
)
def update_regression_figures(selected_year: str) -> tuple[go.Figure, go.Figure]:
    """Met à jour les graphiques de régression quand le filtre d'année change."""
    scatter_fig = build_regression_scatter_figure(regression_predictions, selected_year)
    residuals_fig = build_regression_residuals_figure(regression_predictions, selected_year)
    return scatter_fig, residuals_fig


if __name__ == "__main__":
    app.run(debug=True)
