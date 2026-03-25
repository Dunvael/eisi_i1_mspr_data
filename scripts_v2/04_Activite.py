import pandas as pd
from pathlib import Path
import unicodedata

# ==============================================================================
# CONFIG
# ==============================================================================
BASE_DIR = Path(".")

FILE_2022 = BASE_DIR / "data_raw" / "2022_raw" / "4. Age_activite" / "base-cc-evol-struct-pop-2022.csv"
FILE_2016 = BASE_DIR / "data_raw" / "2017_raw" / "4. Age_activite" / "base-cc-evol-struct-pop-2016.csv"

DIR_OUTPUT = BASE_DIR / "data_filtered" / "activite"
DIR_OUTPUT.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# OUTILS
# ==============================================================================
def remove_accents(text):
    if pd.isna(text):
        return text
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(text))
        if unicodedata.category(c) != 'Mn'
    )

def read_csv_safe(path):
    for enc in ["utf-8", "cp1252", "latin1"]:
        try:
            df = pd.read_csv(path, sep=";", encoding=enc, low_memory=False)
            print(f"✅ Encodage : {enc}")
            return df
        except:
            continue
    raise ValueError("❌ Impossible de lire le fichier")

def harmonize_columns(df, year):
    """Uniformise colonnes 2016/2022"""
    year_suffix = str(year)[-2:]
    new_cols = {}

    for col in df.columns:
        if col.startswith(f"P{year_suffix}_"):
            new_cols[col] = col.replace(f"P{year_suffix}_", "P_")
        if col.startswith(f"C{year_suffix}_"):
            new_cols[col] = col.replace(f"C{year_suffix}_", "C_")

    return df.rename(columns=new_cols)

def select_columns(df):
    cols_age = [c for c in df.columns if c.startswith("P_")]
    cols_stat = [c for c in df.columns if c.startswith("C_")]
    return ["LIBGEO"] + cols_age + cols_stat

# ==============================================================================
# CLEAN
# ==============================================================================
def clean_dataframe(df, year):
    print(f"🧹 Nettoyage {year}")

    df = harmonize_columns(df, year)

    cols = select_columns(df)
    df = df[[c for c in cols if c in df.columns]]

    df = df.rename(columns={"LIBGEO": "localisation"})

    df["localisation"] = (
        df["localisation"]
        .apply(remove_accents)
        .str.strip()
        .str.title()
    )

    return df

# ==============================================================================
# PROCESS
# ==============================================================================
def process_file(path, year):
    print(f"\n📂 {path}")

    if not path.exists():
        print("❌ Fichier introuvable")
        return None

    df = read_csv_safe(path)
    df_clean = clean_dataframe(df, year)

    output = DIR_OUTPUT / f"CLEAN_activite_{year}.csv"
    df_clean.to_csv(output, sep=";", index=False, encoding="utf-8-sig")

    print(f"✅ Export : {output}")
    return df_clean

# ==============================================================================
# RUN
# ==============================================================================
def run():
    print("🚀 ETL Activité")

    process_file(FILE_2022, 2022)
    process_file(FILE_2016, 2016)

    print("🎯 Terminé")

if __name__ == "__main__":
    run()