#!/bin/bash

set -e

echo "======================================================"
echo "LANCEMENT DU PIPELINE MSPR BIG DATA"
echo "======================================================"

echo ""
echo "1. Nettoyage des données (2022)"
echo "------------------------------------------------------"

python3 "2. cleaning_scripts_2022/00_insee_code_referentiel.py"
python3 "2. cleaning_scripts_2022/01_revenus_2022.py"
python3 "2. cleaning_scripts_2022/02_Taux_chomage_2022.py"
python3 "2. cleaning_scripts_2022/03_Categorie_sociale_2022.py"
python3 "2. cleaning_scripts_2022/04_Densite_population_2022.py"
python3 "2. cleaning_scripts_2022/05_Demographie_2022.py"
python3 "2. cleaning_scripts_2022/06_Taux_immigration_2022.py"
python3 "2. cleaning_scripts_2022/07_Associations_2022.py"
python3 "2. cleaning_scripts_2022/08_Creation_entreprises_2022.py"
python3 "2. cleaning_scripts_2022/09_criminalite_diff_ndiff_2022.py"
python3 "2. cleaning_scripts_2022/10_Y_Resultats_2022_pres_t1.py"

echo ""
echo "2. Génération du dataset d'entraînement (2022)"
echo "------------------------------------------------------"

python3 ML/Train_dataframe.py

echo ""
echo "3. Entraînement et évaluation des modèles"
echo "------------------------------------------------------"

python3 ML/test_multi_ml.py

echo ""
echo "4. Nettoyage des données (2024)"
echo "------------------------------------------------------"

python3 "5. cleaning_scripts_2024/00_referentiel_commune_22_24.py"
python3 "5. cleaning_scripts_2024/01.1_deces_2024.py"
python3 "5. cleaning_scripts_2024/01.2_naissances_2024.py"
python3 "5. cleaning_scripts_2024/01.3_population_densite_2024.py"
python3 "5. cleaning_scripts_2024/02_Criminalite_2024.py"
python3 "5. cleaning_scripts_2024/03_tranches_age24.py"
python3 "5. cleaning_scripts_2024/04_Revenus_24.py"
python3 "5. cleaning_scripts_2024/05_chomage24.py"
python3 "5. cleaning_scripts_2024/06_associations_2024.py"
python3 "5. cleaning_scripts_2024/07_creations_entreprises_2024.py"
python3 "5. cleaning_scripts_2024/08_immigration_2024.py"
python3 "5. cleaning_scripts_2024/09_categories_sociales_2024.py"
python3 "5. cleaning_scripts_2024/10_nom_dep.py"

echo ""
echo "5. Génération du dataset de prédiction 2024"
echo "------------------------------------------------------"

python3 "5. cleaning_scripts_2024/create_prediction_dataframe_2024.py"

echo ""
echo "6. Prédiction 2024 avec le meilleur modèle + Graphiques"
echo "------------------------------------------------------"

python3 "5. cleaning_scripts_2024/predict_2024.py"
python3 ML/heatmap.py
python3 ML/carte_choroplethe.py
python3 "5. cleaning_scripts_2024/check_results.py"

echo ""
echo "======================================================"
echo " PIPELINE MSPR TERMINÉ AVEC SUCCÈS"
echo "======================================================"
