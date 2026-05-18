from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html


BASE_DIR = Path("artifacts")

CLASSIFICATION_REPORTS_DIR = BASE_DIR / "classification" / "reports"
CLASSIFICATION_PREDICTIONS_DIR = BASE_DIR / "classification" / "predictions"

LEADERBOARD_PATH = CLASSIFICATION_REPORTS_DIR / "leaderboard_classification.csv"
BEST_SUMMARY_PATH = CLASSIFICATION_REPORTS_DIR / "best_model_classification_summary.json"


def read_csv_if_exists(path):
    if path.exists():
        return pd.read_csv(path)
    return None


def read_json_if_exists(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def empty_fig(title):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{
            "text": "Aucune donnée disponible. Lance d'abord ton script d'entraînement.",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16}
        }],
        height=450
    )
    return fig


def load_data():
    leaderboard = read_csv_if_exists(LEADERBOARD_PATH)
    best_summary = read_json_if_exists(BEST_SUMMARY_PATH)

    predictions = None

    if best_summary:
        model_name = best_summary.get("modele") or best_summary.get("model")
        if model_name:
            pred_path = CLASSIFICATION_PREDICTIONS_DIR / f"predictions_{model_name}.csv"
            predictions = read_csv_if_exists(pred_path)

    return leaderboard, best_summary, predictions


def build_leaderboard_chart(leaderboard):
    if leaderboard is None or leaderboard.empty:
        return empty_fig("Comparaison des modèles")

    leaderboard = leaderboard.copy()

    if "modele" in leaderboard.columns:
        model_col = "modele"
    elif "model" in leaderboard.columns:
        model_col = "model"
    else:
        return empty_fig("Comparaison des modèles")

    metric_cols = [
        col for col in ["accuracy", "f1_weighted", "accuracy_test", "f1_weighted_test"]
        if col in leaderboard.columns
    ]

    if not metric_cols:
        return empty_fig("Comparaison des modèles")

    plot_df = leaderboard[[model_col] + metric_cols].melt(
        id_vars=model_col,
        value_vars=metric_cols,
        var_name="métrique",
        value_name="score"
    )

    fig = px.bar(
        plot_df,
        x=model_col,
        y="score",
        color="métrique",
        barmode="group",
        text_auto=".2f",
        title="Comparaison des performances des modèles"
    )

    fig.update_layout(
        height=500,
        yaxis_title="Score",
        xaxis_title="Modèle",
        yaxis=dict(range=[0, 1])
    )

    return fig


def build_confusion_matrix(predictions):
    if predictions is None or predictions.empty:
        return empty_fig("Matrice de confusion")

    if "y_true" not in predictions.columns or "y_pred" not in predictions.columns:
        return empty_fig("Matrice de confusion")

    labels = sorted(
        set(predictions["y_true"].astype(str))
        | set(predictions["y_pred"].astype(str))
    )

    matrix = pd.crosstab(
        predictions["y_true"].astype(str),
        predictions["y_pred"].astype(str),
        rownames=["Réel"],
        colnames=["Prédit"]
    )

    matrix = matrix.reindex(index=labels, columns=labels, fill_value=0)

    fig = px.imshow(
        matrix,
        text_auto=True,
        aspect="auto",
        title="Matrice de confusion du meilleur modèle"
    )

    fig.update_layout(
        height=550,
        xaxis_title="Classe prédite",
        yaxis_title="Classe réelle"
    )

    return fig


def build_prediction_distribution(predictions):
    if predictions is None or predictions.empty:
        return empty_fig("Répartition des prédictions")

    if "y_pred" not in predictions.columns:
        return empty_fig("Répartition des prédictions")

    count_df = predictions["y_pred"].astype(str).value_counts().reset_index()
    count_df.columns = ["classe", "nombre"]

    fig = px.bar(
        count_df,
        x="classe",
        y="nombre",
        text_auto=True,
        title="Répartition des classes prédites"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Classe prédite",
        yaxis_title="Nombre de prédictions"
    )

    return fig


def build_real_distribution(predictions):
    if predictions is None or predictions.empty:
        return empty_fig("Répartition réelle")

    if "y_true" not in predictions.columns:
        return empty_fig("Répartition réelle")

    count_df = predictions["y_true"].astype(str).value_counts().reset_index()
    count_df.columns = ["classe", "nombre"]

    fig = px.bar(
        count_df,
        x="classe",
        y="nombre",
        text_auto=True,
        title="Répartition réelle des classes"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Classe réelle",
        yaxis_title="Nombre de lignes"
    )

    return fig


leaderboard, best_summary, predictions = load_data()

best_model_name = "Non disponible"
best_f1 = None

if best_summary:
    best_model_name = (
        best_summary.get("modele")
        or best_summary.get("model")
        or "Non disponible"
    )
    best_f1 = (
        best_summary.get("f1_weighted")
        or best_summary.get("f1_weighted_test")
    )


app = Dash(__name__)
app.title = "Comparatif visuel des modèles"

app.layout = html.Div(
    style={
        "padding": "25px",
        "fontFamily": "Arial",
        "backgroundColor": "#f7f7f7"
    },
    children=[
        html.H1("Comparatif visuel des modèles de classification"),

        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "15px",
                "borderRadius": "10px",
                "marginBottom": "20px"
            },
            children=[
                html.H2("Résumé"),
                html.P(f"Meilleur modèle : {best_model_name}"),
                html.P(
                    f"F1-score pondéré : {round(best_f1 * 100, 2)} %"
                    if best_f1 is not None
                    else "F1-score pondéré : Non disponible"
                )
            ]
        ),

        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "15px",
                "borderRadius": "10px",
                "marginBottom": "20px"
            },
            children=[
                dcc.Graph(figure=build_leaderboard_chart(leaderboard))
            ]
        ),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "20px",
                "marginBottom": "20px"
            },
            children=[
                html.Div(
                    style={
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "10px"
                    },
                    children=[
                        dcc.Graph(figure=build_real_distribution(predictions))
                    ]
                ),
                html.Div(
                    style={
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "10px"
                    },
                    children=[
                        dcc.Graph(figure=build_prediction_distribution(predictions))
                    ]
                ),
            ]
        ),

        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "15px",
                "borderRadius": "10px"
            },
            children=[
                dcc.Graph(figure=build_confusion_matrix(predictions))
            ]
        )
    ]
)


if __name__ == "__main__":
    app.run(debug=True)