#!/bin/bash

set -e

echo "======================================================"
echo "LANCEMENT DU PIPELINE MSPR BIG DATA"
echo "======================================================"

echo ""
echo "1. Nettoyage des données (2022)"
echo "------------------------------------------------------"

python3 cleaning_scripts_2022/00_insee_code_referentiel.py
python3 cleaning_scripts_2022/01_Revenu_median.py
python3 cleaning_scripts_2022/02_Taux_chomage.py
python3 cleaning_scripts_2022/03_Categorie_sociale.py
python3 cleaning_scripts_2022/04_Densite_population.py
python3 cleaning_scripts_2022/05_Demographie.py
python3 cleaning_scripts_2022/06_Taux_immigration.py
python3 cleaning_scripts_2022/07_Associations.py
python3 cleaning_scripts_2022/08_Creation_entreprises.py
python3 cleaning_scripts_2022/09_criminalite_diff_ndiff.py
python3 cleaning_scripts_2022/Y_Resultats_2022_pres_t1.py

echo ""
echo "2. Génération du dataset d'entraînement (2022)"
echo "------------------------------------------------------"

python3 cleaning_scripts_2022/create_training_dataframe_2022.py

echo ""
echo "3️. Entraînement et évaluation des modèles"
echo "------------------------------------------------------"
python3 cleaning_scripts_2022/train_models.py

echo ""
echo "4. Nettoyage des données (2024)"
echo "------------------------------------------------------"

python3 cleaning_scripts_2024/00_referentiel_commune_22_24.py
python3 cleaning_scripts_2024/01.1_deces_2024.py
python3 cleaning_scripts_2024/01.2_naissances_2024.py
python3 cleaning_scripts_2024/01.3_population_densite_2024.py
python3 cleaning_scripts_2024/02_Criminalite_2024.py
python3 cleaning_scripts_2024/03_tranches_age24.py
python3 cleaning_scripts_2024/04_Revenus_24.py
python3 cleaning_scripts_2024/05_chomage24.py
python3 cleaning_scripts_2024/06_associations_2024.py
python3 cleaning_scripts_2024/07_creations_entreprises_2024.py
python3 cleaning_scripts_2024/08_immigration_2024.py
python3 cleaning_scripts_2024/09_categories_sociales_2024.py

echo ""
echo "5. Génération du dataset de prédiction 2024"
echo "------------------------------------------------------"

python3 cleaning_scripts_2024/create_prediction_dataframe_2024.py

echo ""
echo "6. Prédiction 2024 avec le meilleur modèle"
echo "------------------------------------------------------"
python3 predict_2024.py

echo ""
echo "======================================================"
echo " PIPELINE MSPR TERMINÉ AVEC SUCCÈS"
echo "======================================================"