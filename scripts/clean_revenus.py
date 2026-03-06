import pandas as pd
import numpy as np
import os
import unicodedata

# ==========================================
# CONFIGURATION
# ==========================================
# Noms des fichiers sources (à adapter avec les vrais noms)
FILE_2017 = "insee_revenus_2017.csv"
FILE_2021 = "insee_revenus_2021.csv"
OUTPUT_FILENAME = "revenus_pauvrete_2017_2021_clean.csv"

current_dir = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(current_dir, "..", "data_clean")
output_file = os.path.join(output_folder, OUTPUT_FILENAME)

os.makedirs(output_folder, exist_ok=True)

# ==========================================
# FONCTIONS DE NETTOYAGE
# ==========================================
def remove_accents(text):
    if pd.isna(text):
        return text
    text = str(text)
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

def clean_insee_values(val):
    """
    Remplace le secret statistique de l'INSEE ('s', 'so', 'nd', 'ns') par du vide (NaN)
    et remplace les virgules par des points pour la conversion numérique.
    """
    if pd.isna(val):
        return np.nan
    val = str(val).strip().lower()
    if val in ['s', 'so', 'nd', 'ns', 'n.d.', '']:
        return np.nan
    # Remplacer les virgules françaises par des points
    val = val.replace(',', '.')
    return val

# ==========================================
# FONCTION DE TRAITEMENT PAR ANNÉE
# ==========================================
def process_year(filename, year):
    filepath = os.path.join(current_dir, "..", "data_raw", filename)
    print(f"Traitement de l'année {year} : {filename}...")
    
    try:
        df = pd.read_csv(filepath, sep=';', low_memory=False, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, sep=';', low_memory=False, encoding='latin-1')
    
    # 1. Identifier la colonne LIBCOM
    col_libcom = [c for c in df.columns if c.upper() == "LIBCOM"]
    if not col_libcom:
        # Fallback si elle s'appelle autrement (ex: Libellé)
        col_libcom = [c for c in df.columns if "lib" in c.lower()][0]
    else:
        col_libcom = col_libcom[0]

    # 2. Sélectionner les colonnes par leurs indices (A=0, B=1...)
    # Colonnes demandées : LIBCOM, E(4), F(5), I(8), L à T (11 à 19), W à AB (22 à 27)
    indices_to_keep = [4, 5, 8] + list(range(11, 20)) + list(range(22, 28))
    
    # On récupère les noms des colonnes correspondant à ces indices
    cols_by_index = [df.columns[i] for i in indices_to_keep if i < len(df.columns)]
    
    # On crée le dataset filtré
    cols_finales = [col_libcom] + cols_by_index
    df_filtered = df[cols_finales].copy()
    
    # 3. Renommer les colonnes (Adaptation logique basée sur les fichiers INSEE classiques)
    # L'INSEE a toujours la même structure. J'attribue des noms explicites.
    new_names = {col_libcom: "localisation"}
    
    # Mapping générique basé sur tes index (à vérifier avec ton vrai fichier)
    col_names = [
        "nb_menages", "nb_personnes", "mediane_niveau_vie", 
        "decile_1", "decile_2", "decile_3", "decile_4", "decile_6", 
        "decile_7", "decile_8", "decile_9", "rapport_interdecile",
        "part_salaires", "part_chomage", "part_retraites", 
        "part_patrimoine", "part_prestations_sociales", "part_impots"
    ]
    
    for i, col in enumerate(cols_by_index):
        if i < len(col_names):
            new_names[col] = col_names[i]
            
    df_filtered = df_filtered.rename(columns=new_names)
    
    # 4. Nettoyage de la localisation
    df_filtered["localisation"] = df_filtered["localisation"].apply(remove_accents).str.title()
    
    # 5. Appliquer le nettoyage INSEE (s, nd, ns -> NaN) et convertir en nombres
    cols_numeriques = [c for c in df_filtered.columns if c != "localisation"]
    for col in cols_numeriques:
        df_filtered[col] = df_filtered[col].apply(clean_insee_values)
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')
    
    # 6. RÈGLE SPÉCIFIQUE : RAPPORT INTERDÉCILE ENTRE 10 ET 100
    if "rapport_interdecile" in df_filtered.columns:
        # On remplace les valeurs aberrantes (entre 10 et 100) par NaN (Null) 
        # plutôt que de supprimer toute la ville, pour ne pas perdre les autres données
        mask_aberrant = (df_filtered["rapport_interdecile"] >= 10) & (df_filtered["rapport_interdecile"] <= 100)
        df_filtered.loc[mask_aberrant, "rapport_interdecile"] = np.nan
        nb_exclus = mask_aberrant.sum()
        print(f" -> {nb_exclus} valeurs aberrantes exclues pour le rapport interdécile (mises à NULL).")
    
    df_filtered["annee"] = year
    return df_filtered

# ==========================================
# EXÉCUTION
# ==========================================
df_2017 = process_year(FILE_2017, 2017)
df_2021 = process_year(FILE_2021, 2021)

# Concaténer les deux années
df_final = pd.concat([df_2017, df_2021], ignore_index=True)

# Sauvegarde
print(f"Sauvegarde en cours vers : {output_file}")
df_final.to_csv(output_file, index=False)
print("Succès ! Fichier des revenus nettoyé.")