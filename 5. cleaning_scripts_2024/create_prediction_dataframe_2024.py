import pandas as pd
import sqlite3
import time
import os
from pathlib import Path
import sys

# Importation de 'rich' pour des terminaux magnifiques
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich import print as rprint

# Initialisation de la console
console = Console()
start_time = time.time()

console.print(Panel.fit("[bold magenta]🚀 DÉMARRAGE DU PIPELINE ETL : MASTER DATASET 2024 (ADVANCED)[/bold magenta]", border_style="cyan"))

# =========================================================
# 1. CONFIGURATION
# =========================================================
BASE_DIR = Path(".")
DATA_CLEANED = BASE_DIR / "data_cleaned" / "2024"
OUTPUT_CSV = DATA_CLEANED / "DATASET_ML_2024.csv"
DB_PATH = BASE_DIR / "mspr_database.db"

# =========================================================
# 2. CHARGEMENT DU RÉFÉRENTIEL
# =========================================================
console.print("\n[bold blue][1/5] LECTURE DU RÉFÉRENTIEL...[/bold blue]")

ref_path = DATA_CLEANED / "00_referentiel_communes_22_24_clean.csv"

if not ref_path.exists():
    console.print(f"[bold red]❌ Fichier introuvable : {ref_path}[/bold red]")
    sys.exit(1)

# =========================================================
# FONCTION DE NETTOYAGE DES CODES INSEE
# =========================================================
def clean_insee(code):
    """
    Nettoyage ultra robuste des codes INSEE :
    - supprime les .0
    - garde uniquement les chiffres
    - ajoute les zéros initiaux
    - retourne toujours 5 caractères
    """
    if pd.isna(code):
        return None

    # Conversion en texte + suppression espaces
    code = str(code).strip()

    # Suppression du .0 final
    if code.endswith(".0"):
        code = code[:-2]

    # Conservation uniquement des chiffres
    code = ''.join(filter(str.isdigit, code))

    # Ajout des zéros initiaux
    return code.zfill(5)

# =========================================================
# LECTURE DU RÉFÉRENTIEL
# =========================================================
df_master = pd.read_csv(
    ref_path,
    sep=";",
    dtype=str
)

# =========================================================
# NETTOYAGE DES CODES INSEE
# =========================================================
for col in ["code_insee_2022", "code_insee_2024"]:
    if col in df_master.columns:
        df_master[col] = df_master[col].apply(clean_insee)

# =========================================================
# INFORMATIONS DE CONTRÔLE
# =========================================================
initial_rows = len(df_master)

console.print(
    f"  [green]✔ Référentiel chargé : {initial_rows:,} communes (Ligne de base)[/green]"
)

# Vérification rapide
console.print(
    f"  [cyan]Exemple INSEE 2022 :[/cyan] {df_master['code_insee_2022'].iloc[0]}"
)

console.print(
    f"  [cyan]Exemple INSEE 2024 :[/cyan] {df_master['code_insee_2024'].iloc[0]}"
)

# =========================================================
# 3. FUSION DES DATAMARTS & TRACKING
# =========================================================
console.print("\n[bold blue][2/5] INTÉGRATION DES DATAMARTS...[/bold blue]")

datasets = [
    ("01_Densite_population/01.3_population_densite_2024_clean.csv", ["population", "densite"]),
    ("10_nom_departement.csv", ["nom_departement"]),
    ("02_Criminalite/02_criminalite_diff_ndiff_2024_cleaned.csv", [ "taux_cambriolages_logement", "taux_violences_intrafamiliales", "taux_degradations", "taux_trafic_stupefiants", "taux_usage_stupefiants", "taux_violences_sexuelles", "taux_vols_avec_armes", "taux_vols_vehicule", "taux_vols_violents_sans_arme" ]),
    ("03_Demographie/03_tranches_age_2024_clean.csv", ["pct_jeunes", "pct_seniors", "age_median"]),
    ("04_Revenus/04_revenus_2024_estim_clean.csv", ["revenu_estime_2024"]),
    ("05_Chomage/05_chomage_2024_clean.csv", ["taux_chomage_15_64"]),
    ("06_Associations/06_associations_2024_clean.csv", ["densite_asso_1000_hab"]),
    ("07_Entreprises/07_creations_entreprises_2024_clean.csv", ["taux_creation_entreprises_1000_hab"]),
    ("08_Immigration/08_immigration_2024_clean.csv", ["taux_immigration_pct"]),
    ("09_CS/09_categories_sociales_2024_clean.csv", ["pourcentage_agri", "pourcentage_cadres", "pourcentage_employes", "pourcentage_ouvriers"])
]

table_fusion = Table(title="Audit des Fusions (Jointures sur Référentiel)", show_header=True, header_style="bold magenta")
table_fusion.add_column("Datamart", style="cyan")
table_fusion.add_column("Statut", justify="center")
table_fusion.add_column("Taux de Match", justify="right")
table_fusion.add_column("Doublons", justify="right")

for file_rel_path, cols in track(datasets, description="[cyan]Traitement des fichiers...[/cyan]"):
    path = DATA_CLEANED / file_rel_path
    nom_court = file_rel_path.split('/')[0]
    
    if path.exists():
        df_temp = pd.read_csv(path, sep=";", dtype=str)
        
        # UTILISATION DE LA FONCTION ROBUSTE POUR NETTOYER LE CODE INSEE
        df_temp["code_insee_2024"] = df_temp["code_insee_2024"].apply(clean_insee)
        # Tracking des doublons
        doublons_avant = len(df_temp)
        df_temp = df_temp.drop_duplicates(subset=['code_insee_2024'])
        doublons_retires = doublons_avant - len(df_temp)
        str_doublons = f"[red]{doublons_retires}[/red]" if doublons_retires > 0 else "[green]0[/green]"
        
        # Tracking du taux de Match
        communes_in_master = df_master['code_insee_2024'].isin(df_temp['code_insee_2024']).sum()
        match_rate = (communes_in_master / initial_rows) * 100
        
        if match_rate == 100:
            str_match = f"[green]{match_rate:.1f}%[/green]"
        elif match_rate > 95:
            str_match = f"[yellow]{match_rate:.1f}%[/yellow]"
        else:
            str_match = f"[red]{match_rate:.1f}%[/red]"

        # Fusion
        df_master = pd.merge(df_master, df_temp[["code_insee_2024"] + cols], on="code_insee_2024", how="left")
        
        table_fusion.add_row(nom_court, "[green]✔ OK[/green]", str_match, str_doublons)
    else:
        table_fusion.add_row(nom_court, "[red]❌ MANQUANT[/red]", "-", "-")

console.print("\n")
console.print(table_fusion)

# =========================================================
# 4. NETTOYAGE, DATA QUALITY ET TYPAGE DES VARIABLES
# =========================================================
console.print("\n[bold blue][3/5] DATA QUALITY & IMPUTATION...[/bold blue]")
numeric_cols = [c for c in df_master.columns if c not in ["code_insee_2024", "nom_commune_2024", "nom_departement", "annee", "code_insee_2022"]]

df_master[numeric_cols] = df_master[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Tracking des NaNs par colonne
table_nan = Table(title="Audit des Valeurs Manquantes (NaN)", show_header=True, header_style="bold yellow")
table_nan.add_column("Variable", style="cyan")
table_nan.add_column("NaN (Avant)", justify="right")
table_nan.add_column("Statut Imputation", justify="center")

nan_total = df_master[numeric_cols].isna().sum().sum()

if nan_total > 0:
    for col in numeric_cols:
        nans = df_master[col].isna().sum()
        if nans > 0:
            # Imputation par la médiane
            df_master[col] = df_master[col].fillna(df_master[col].median())
            table_nan.add_row(col, f"[red]{nans}[/red]", "[green]✔ Médiane[/green]")
    console.print(table_nan)
    console.print("  [bold green]✔ Dataset 100% complet pour le Machine Learning ![/bold green]")
else:
    console.print("  [bold green]✔ Aucune valeur manquante détectée sur l'ensemble du Master ![/bold green]")

# --- AJOUT : FORMATAGE STRICT DES ENTIERS ET DÉCIMALES ---
cols_entieres = ["population"] 

for col in numeric_cols:
    if col in cols_entieres:
        # Int64 garantit un vrai format entier sans .0 (ex: 1500)
        df_master[col] = df_master[col].round(0).astype('Int64')
    else:
        # Les autres variables (taux, pourcentages, revenus) sont des décimales
        df_master[col] = df_master[col].round(2)

# =========================================================
# 5. EXPORT CSV & SQLITE
# =========================================================
console.print("\n[bold blue][4/5] SAUVEGARDE & EXPORT...[/bold blue]")

# S'assurer que le dossier final existe
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# L'ajout de decimal="," est la clé pour Power BI
df_master.to_csv(OUTPUT_CSV, sep=";", decimal=",", index=False, encoding="utf-8-sig")
file_size_mb = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
console.print(f"  [green]✔ Fichier CSV généré ({file_size_mb:.2f} MB)[/green]")

try:
    conn = sqlite3.connect(DB_PATH)
    
    # Sécurisation des types pour SQLite (qui gère moins bien le Int64 de Pandas)
    df_sql = df_master.copy()
    for col in numeric_cols:
        if col not in cols_entieres:
            df_sql[col] = df_sql[col].astype(float)
            
    df_sql.to_sql("prediction_2024", conn, if_exists="replace", index=False)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM prediction_2024")
    row_count = cursor.fetchone()[0]
    conn.close()
    console.print(f"  [green]✔ Base SQLite mise à jour : {row_count:,} entrées.[/green]")
except Exception as e:
    console.print(f"  [bold red]❌ Erreur SQLite : {e}[/bold red]")

# =========================================================
# 6. APERÇU DES DONNÉES
# =========================================================
console.print("\n[bold blue][5/5] APERÇU DU MASTER DATASET...[/bold blue]")
table_preview = Table(show_header=True, header_style="bold cyan")

# On limite le preview à 6 colonnes pour que ça rentre dans le terminal
preview_cols = ["code_insee_2024", "nom_commune_2024", "nom_departement", "population", "taux_chomage_15_64", "revenu_estime_2024"]
preview_cols = [c for c in preview_cols if c in df_master.columns]

for col in preview_cols:
    table_preview.add_column(col)

for _, row in df_master.head(5).iterrows():
    table_preview.add_row(*[str(row[c]) for c in preview_cols])

console.print(table_preview)

# =========================================================
# 7. RAPPORT D'EXÉCUTION (PANEL)
# =========================================================
exec_time = time.time() - start_time
memory_usage = df_master.memory_usage(deep=True).sum() / (1024 * 1024)

rapport = f"""
[bold cyan]Temps d'exécution[/bold cyan]     : {exec_time:.2f} secondes
[bold cyan]Mémoire RAM allouée[/bold cyan]   : {memory_usage:.2f} MB
[bold cyan]Communes consolidées[/bold cyan]  : {len(df_master):,}
[bold cyan]Variables ML générées[/bold cyan] : {df_master.shape[1]}
[bold cyan]Format de Sortie[/bold cyan]      : CSV (Power BI) + SQLite (Machine Learning)
"""

console.print("\n")
console.print(Panel(rapport, title="[bold magenta]📊 RAPPORT D'AUDIT FINAL - PIPELINE RÉUSSI[/bold magenta]", border_style="green"))