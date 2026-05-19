# MSPR Data

---

## *Réalisation du projet*

* AMAZOUZ Anas
* EL HOUZI Abdelmounaïm
* LE ROUX Dunvael
* YOULA Moussa

*Date de rendu* : 22 Mai 2026  
*Date de soutenance* : 29 Mai 2026

---

## Prérequis

* Python 3.11+
* Téléchargement des datasets d'entraînement (2022) et de prédiction (2024) dans le dossier xx → *cf. Sources des datasets*
* Préparation de l'environnement Python 'dépendances) → fichier `requirements.txt` à lancer avec le script py_libraries.sh (placé à la racine du projet)
* Script de déploiment automatisé des scripts ETL Python

---

## Déployer le pipeline ETL

1. Clôner le dépôt GitHub avec son arborescence :

```Git Bash
git clone https://github.com/Dunvael/eisi_i1_mspr_data.git
```

2. Télécharger et enregistrer les datasets
3. Donner les autorisations d'exécution aux fichiers py_libraries.sh et mspr.sh :
* `chmod +x py_libraries.sh`
* `chmod +x mspr.sh`
4. Executer le script py_libraries.sh (installation des dépendances Python nécessaires → fichier `requirements.txt`) :

```Git Bash
./py_libraries.sh
```

5. Executer le script mspr.sh :

```Git Bash
./mspr.sh
```

Le script mspr.sh permet de déployer l'intégralité du pipeline ETL :

* Génération du dataset d'entrainement (2022)
   * Nettoyage des données collectées
   * Transformation des données
   * Extraction des données
* Entraînement des différents modèles de Machine Learning et vérifications
* Sélection du meilleur modèle de Machine Learning
* Génération du dataset de prédiction (2024)
   * Nettoyage des données collectées
   * Transformation des données
   * Extraction des données
* Prédiction du modèle de Machine Learning pour répondre à la problématique de classification électorale et vérifications
* Affichage des résultats

---

## Sources des datasets

### Datasets bruts
- Datasets bruts à télécharger sur : <https://drive.google.com/drive/u/0/folders/1ctrtEDFBT0UUJKnAV3cDtuv0cvZm6NUx>

### Datasets nettoyés
- Datasets nettoyés disponibles dans le dossier `data_cleaned`

### Tableau des sources des datasets

#### Année 2022

| Nom du dataset | Critère | Lien |
|---|---|---|
| Code officiel géographique au 1er janvier 2022 | Codes INSEE | [Référentiel des codes communes de France 2022 - INSEE](https://www.insee.fr/fr/information/6051727) |
| Table de passage annuelle 2025 | Conversion des codes communes | [Tables de passage des communes](https://www.insee.fr/fr/information/7671867) |
| Base niveau communes en 2021 - y compris arrondissements municipaux | Revenus médians | [Revenus médians](https://www.insee.fr/fr/statistiques/6453850) |
| NAT2 – Population de 15 ans ou plus par sexe, type d'activité et nationalité | Taux de chômage | [Taux de chômage](https://www.insee.fr/fr/statistiques/8205621) |
| Évolution et structure de la population en 2022 - Commune - France hors Mayotte | Catégorie sociale | [Catégorie sociale](https://www.insee.fr/fr/statistiques/8205621) |
| Liste des communes de France 2022 et de leurs codes associés | Densité de population | [Densité de population](https://www.data.gouv.fr/fr/datasets/communes-de-france-base-des-codes-postaux/) |
| Population selon le sexe et l'âge quinquennal de 1968 à 2022 | Démographie | [Démographie](https://www.insee.fr/fr/statistiques/2381472) |
| NAT2 – Population de 15 ans ou plus par sexe, type d'activité et nationalité | Taux d’immigration | [Taux d’immigration](https://www.insee.fr/fr/statistiques/8205621) |
| rna-2024.xlsx | Nombre de créations d’associations | [RNA Associations](https://www.data.gouv.fr/fr/datasets/repertoire-national-des-associations/) |
| Créations d'entreprises au niveau communal et supra communal | Nombre de créations d’entreprises | [Créations d’entreprises](https://www.insee.fr/fr/statistiques/2011101) |
| Base statistique communale de la délinquance enregistrée | Criminalité | [Criminalité](https://www.data.gouv.fr/fr/datasets/base-statistique-communale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales/) |
| Résultats par candidats | Résultats du 1er tour des élections présidentielles 2022 | [Résultats élections présidentielles 2022](https://www.data.gouv.fr/fr/datasets/resultats-des-elections-presidentielles-2022/) |

#### Année 2024

| Nom du dataset | Critère | Lien |
|---|---|---|
| Code officiel géographique au 1er janvier 2024 | Codes INSEE | [Référentiel des codes communes de France 2024 - INSEE](https://www.insee.fr/fr/information/7766585) |
| Table de passage annuelle 2025 | Conversion des codes communes | [Tables de passage des communes](https://www.insee.fr/fr/information/7671867) |
| Base niveau communes en 2021 - y compris arrondissements municipaux | Revenus médians | [Revenus médians](https://www.insee.fr/fr/statistiques/6453850) |
| Inscrits à France Travail - Données communales | Taux de chômage | [France Travail - chômage communal](https://www.data.gouv.fr/fr/datasets/inscrits-a-france-travail-donnees-communales/) |
| Évolution et structure de la population en 2022 - Commune - France hors Mayotte | Catégorie sociale | [Catégorie sociale](https://www.insee.fr/fr/statistiques/8205621) |
| Communes et villes de France 2025 | Densité de population | [Communes de France](https://www.data.gouv.fr/fr/datasets/communes-de-france-base-des-codes-postaux/) |
| Population selon le sexe et l'âge quinquennal de 1968 à 2022 | Démographie | [Démographie](https://www.insee.fr/fr/statistiques/2381472) |
| NAT2 – Population de 15 ans ou plus par sexe, type d'activité et nationalité | Taux d’immigration | [Taux d’immigration](https://www.insee.fr/fr/statistiques/8205621) |
| rna-2024.xlsx | Nombre de créations d’associations | [RNA Associations](https://www.data.gouv.fr/fr/datasets/repertoire-national-des-associations/) |
| Créations d'entreprises au niveau communal et supra communal | Nombre de créations d’entreprises | [Créations d’entreprises](https://www.insee.fr/fr/statistiques/2011101) |
| Base statistique communale de la délinquance enregistrée | Criminalité | [Criminalité](https://www.data.gouv.fr/fr/datasets/base-statistique-communale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales/) |

## Datasets utilisés pour les estimations 2024

| Nom du dataset | Utilisation | Lien |
|---|---|---|
| Indicateurs sur les revenus et la pauvreté au niveau local en 2023 | Estimation des revenus médians 2024 | [Revenus et pauvreté 2023](https://www.insee.fr/fr/statistiques/8282210) |
| Nombre de décès annuels par commune de 2008 à 2024 | Estimation démographie / immigration / catégorie sociale | [Décès par commune](https://www.data.gouv.fr/fr/datasets/nombre-de-deces-annuels-par-commune/) |
| Nombre de naissances annuelles par commune de 2008 à 2024 | Estimation démographie / immigration / catégorie sociale | [Naissances par commune](https://www.data.gouv.fr/fr/datasets/nombre-de-naissances-annuelles-par-commune/) |
| Populations de référence en 2023 | Estimation démographie 2024 | [Populations de référence](https://www.insee.fr/fr/statistiques/7756722) |
| Base statistique communale de la délinquance enregistrée | Récupération population 2024 | [Criminalité](https://www.data.gouv.fr/fr/datasets/base-statistique-communale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales/) |

---

## Documentation et fichiers

* Sujet de la MSPR Big Data
* Grille de notation de la MSPR Big Data
* Livrable .pdf "Rapport...." contenant les étapes de réalisation de la MSPR ainsi que les sources des datasets utilisés pour mener à bien le projet POC.
* Fichier .pbix de visualisation des données de prédiction
* Données structurées SQLite

---
