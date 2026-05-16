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

* Dépendances Python → fichier `requirements.txt` à lancer avec xx.sh
* Téléchargement des datasets d'entraînement (2022) et de prédiction (2024) dans le dossier xx → *cf. Sources des datasets*
* Script de déploiment automatisé des scripts ETL Python

---

## Déployer le pipeline ETL

1. Clôner le dépôt GitHub avec son arborescence :

```Git Bash
git clone https://github.com/Dunvael/eisi_i1_mspr_data.git
```

2. Télécharger et enregistrer les datasets (cf. Sources des datasets) dans le dossier xx.
3. Donner les autorisations d'exécution au fichier xx.sh : `chmod +x xx.sh`
4. Executer le script

```Git Bash
./xx.sh
```

Le script xx.sh permet de déployer l'intégralité du pipeline ETL :

* Installation des dépendances Python nécessaires (fichier `requirements.txt`)
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

## Documentation et fichiers

* Sujet de la MSPR Big Data
* Grille de notation de la MSPR Big Data
* Livrable .pdf "Rapport...." contenant les étapes de réalisation de la MSPR ainsi que les sources des datasets utilisés pour mener à bien le projet POC.
* Fichier .pbix de visualisation des données de prédiction
* Données structurées SQLite

---
