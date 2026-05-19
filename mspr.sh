#!/bin/bash

set -e

echo "======================================"
echo " LANCEMENT DU PIPELINE MSPR BIG DATA"
echo "======================================"

echo ""
echo "1. Nettoyage des données collectées"
echo "--------------------------------------"

python3 scripts/clean_revenus.py
python3 scripts/clean_chomage.py
python3 scripts/clean_categorie_sociale.py
python3 scripts/clean_densite_population.py
python3 scripts/clean_demographie.py
python3 scripts/clean_immigration.py
python3 scripts/clean_associations.py
python3 scripts/clean_entreprises.py
python3 scripts/clean_criminalite.py
python3 scripts/clean_elections.py
python3 scripts/clean_votes_politiques.py

echo ""
echo "2. Génération du dataset d'entraînement 2022"
echo "--------------------------------------"

python3 scripts/create_training_dataframe_2022.py

echo ""
echo "3. Entraînement et évaluation des modèles"
echo "--------------------------------------"

python3 scripts/train_models.py

echo ""
echo "4. Génération du dataset de prédiction 2024"
echo "--------------------------------------"

python3 scripts/create_prediction_dataframe_2024.py

echo ""
echo "5. Prédiction avec le meilleur modèle"
echo "--------------------------------------"

python3 scripts/predict_2024.py

echo ""
echo "======================================"
echo " PIPELINE MSPR TERMINÉ AVEC SUCCÈS"
echo "======================================"
