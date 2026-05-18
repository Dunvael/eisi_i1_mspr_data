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

* Datasets bruts à télécharger sur :
* Datasets nettoyés à télécharger sur :

Tableau des sources des datasets :

...

---

## Documentation et fichiers

* Sujet de la MSPR Big Data
* Grille de notation de la MSPR Big Data
* Livrable .pdf "Rapport...." contenant les étapes de réalisation de la MSPR ainsi que les sources des datasets utilisés pour mener à bien le projet POC.
* Fichier .pbix de visualisation des données de prédiction
* Données structurées SQLite

---
