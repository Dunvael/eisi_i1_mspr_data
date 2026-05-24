import pandas as pd
from pathlib import Path
import sys

# 1. Configuration des chemins : 

# Répertoire racine du projet
BASE_DIR = Path(".")

# Chemin vers le fichier brut fourni par l'INSEE
FILE_RAW_COMMUNES = BASE_DIR / "data_raw" / "2022_raw" / "0_code_insee_2022" / "communes_2022.csv"

# Dossier où sera exporté le fichier nettoyé
DIR_CLEANED = BASE_DIR / "data_cleaned"

# Création du dossier de sortie s'il n'existe pas déjà
DIR_CLEANED.mkdir(parents=True, exist_ok=True)


# 2. Nettoyage du référentiel communes : 

def run_etl():
    print("NETTOYAGE DU REFERENTIEL CODE INSEE")
    
    if not FILE_RAW_COMMUNES.exists():
        print(f"ERREUR : Le fichier {FILE_RAW_COMMUNES} est introuvable.")
        sys.exit(1)

    try:
        #  Étape 1 : Extraction 

        print("Lecture du fichier brut de l'INSEE...")

        # Lecture du fichier CSV brut
        # dtype=str permet de conserver les codes INSEE avec leurs zéros au début
        df = pd.read_csv(FILE_RAW_COMMUNES, sep=",", dtype=str, encoding='utf-8')

        print(f"Données brutes chargées : {len(df):,} lignes.")


        #  Étape 2. Transformation : séléction des colonnes

        # Dictionnaire de correspondance entre les noms INSEE 
        # et les noms utilisés dans notre projet : 
        colonnes_a_garder = {
            'TYPECOM': 'type_commune',
            'COM': 'code_insee',
            'LIBELLE': 'nom_commune',
            'DEP': 'code_departement',
            'REG': 'code_region'
        }

        # On garde uniquement les colonnes présentes dans le fichier : 
        # cela évite une erreur si une colonne est absente : 
        cols_presentes = [col for col in colonnes_a_garder.keys() if col in df.columns]

        # Sélection et renommage des colonnes : 
        df = df[cols_presentes].rename(columns=colonnes_a_garder)



        # Étape 3 : Qualité de la donnée : Gestion des valeurs manquantes

        # Suppression des lignes sans code INSEE : le code INSEE est indispensable pour les jointures futures
        df = df.dropna(subset=["code_insee"])

        # Remplacement des noms de communes manquants
        df["nom_commune"] = df["nom_commune"].fillna("inconnu")


        # Étape 4 : Normalisation des formats : 
        
        print("Formatage des codes INSEE...")

        # Normalisation du code INSEE sur 5 caractères : 
        df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

        # Suppression des espaces inutiles dans les champs texte
        df["nom_commune"] = df["nom_commune"].astype(str).str.strip()
        df["code_departement"] = df["code_departement"].astype(str).str.strip()
        df["code_region"] = df["code_region"].astype(str).str.strip()



        # Étape 5 : Filtrage des arrondissements municipaux 

        # Les arrondissements municipaux de Paris, Lyon et Marseille sont identifiés par le type "ARM".
        # Ils sont donc retirés pour conserver uniquement les communes principales.
        if "type_commune" in df.columns:
            nb_avant = len(df)

            df = df[df["type_commune"] != "ARM"].copy()

            print("\n--- SUPPRESSION ARRONDISSEMENTS MUNICIPAUX ---")
            print("Lignes supprimées :", nb_avant - len(df))
            print("Lignes restantes :", len(df))


        # Étape 6 : Filtrage des DOM/TOM

        # Liste des codes départements ultramarins exclus du périmètre : 
        dom_codes = ["971", "972", "973", "974", "975", "976"]

        nb_avant = len(df)

        # Suppression des communes appartenant aux DOM/TOM
        df = df[
            ~df["code_departement"].isin(dom_codes)
        ].copy()

        print("\n--- SUPPRESSION DOM/TOM ---")
        print("Lignes supprimées :", nb_avant - len(df))
        print("Lignes restantes :", len(df))
        

        # Étape 7 : Suppression des doublons : 

        # Suppression des doublons sur le code INSEE car chaque commune doit être unique dans le référentiel
        df = df.drop_duplicates(subset=["code_insee"])


        # Étape 8 : Contrôle qualité final

        print("\n--- CONTRÔLE DES VALEURS MANQUANTES ---")
        print(df.isna().sum())


        # Contrôle des communes sans département/région
        print("\n--- COMMUNES SANS CODE_DEPARTEMENT OU CODE_REGION ---")

        df_missing_geo = df[
            df["code_departement"].isna() |
            df["code_region"].isna() |
            (df["code_departement"].astype(str).str.lower() == "nan") |
            (df["code_region"].astype(str).str.lower() == "nan")
        ]

        print("Nombre de lignes concernées :", len(df_missing_geo))

        print(df_missing_geo[[
            "type_commune",
            "code_insee",
            "nom_commune",
            "code_departement",
            "code_region"
        ]].head(20))


        # Vérification des types de communes concernés
        # On vérifie que seules les communes déléguées (COMD) et associées (COMA) sont impactées.
        types_attendus = ["COMD", "COMA"]

        df_types_anormaux = df_missing_geo[
            ~df_missing_geo["type_commune"].isin(types_attendus)
        ]

        print("\n--- TYPES ANORMAUX ---")
        print("Nombre :", len(df_types_anormaux))

        print(df_types_anormaux[[
            "type_commune",
            "code_insee",
            "nom_commune",
            "code_departement",
            "code_region"
        ]].head(50))


        # Traitement des communes COMD / COMA
        # Du fait que certaines communes déléguées et associées ne possèdent pas de département/région
        # dans le référentiel brut de l’INSEE.
        #
        # Le département est reconstruit à partir des 2 premiers caractères du code INSEE.

        mask_missing_geo = (
            df["type_commune"].isin(["COMD", "COMA"])
            &
            (
                df["code_departement"].isna() |
                df["code_region"].isna() |
                (df["code_departement"].astype(str).str.lower() == "nan") |
                (df["code_region"].astype(str).str.lower() == "nan")
            )
        )
        
        df.loc[mask_missing_geo, "code_departement"] = (
               df.loc[mask_missing_geo, "code_insee"]
               .astype(str)
               .str[:2]
        )


        # Construction automatique du mapping
        # département -> région
        # à partir des communes déjà valides

        mapping_regions = (
            df[
                df["code_region"].notna() &
                (df["code_region"].astype(str).str.lower() != "nan")
            ][[
                "code_departement",
                "code_region"
            ]]
            .drop_duplicates(subset=["code_departement"])
            .set_index("code_departement")["code_region"]
            .to_dict()
        )

        # Reconstruction de la région

        df.loc[mask_missing_geo, "code_region"] = (
            df.loc[mask_missing_geo, "code_departement"]
            .map(mapping_regions)
        )


        # Contrôle final après reconstruction

        print("\n--- CONTRÔLE APRÈS RECONSTRUCTION ---")

        print(df[[
            "code_departement",
            "code_region"
        ]].isna().sum())

        

        # Étape 9 : Chargement / Export

        # Chemin du fichier nettoyé : 
        chemin_sortie = DIR_CLEANED / "communes_2022_cleaned.csv"

        # Export du dataframe nettoyé au format CSV
        # sep=";" pour compatibilité Excel
        # utf-8-sig pour conserver les accents correctement
        df.to_csv(chemin_sortie, sep=";", index=False, encoding="utf-8-sig")
        
        print(f"SUCCÈS : Fichier nettoyé ! ({len(df):,} communes prêtes)")
        print(f"Fichier disponible ici : {chemin_sortie}")
        
        

    except Exception as e:
        print(f"Une erreur a interrompu le script : {e}")


# Point d'entrée du script : 
if __name__ == "__main__":
    run_etl()