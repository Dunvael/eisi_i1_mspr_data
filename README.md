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
* Script de déploiment automatisé des scripts ETL Python
  * Donner les autorisations d'exécution au fichier xx.sh : `chmod +x xx.sh`
  * Executer le script `./xx.sh`

---

## Déployer le pipeline ETL

Le script xx.sh permet de déployer l'intégralité du pipeline ETL :

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

## Documentation

* Sujet de la MSPR Big Data
* Grille de notation de la MSPR Big Data
* Livrable .pdf "Rapport...." contenant les étapes de réalisation de la MSPR ainsi que les sources des datasets utilisés pour mener à bien le projet POC.

---
