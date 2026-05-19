#!/bin/bash

set -e

echo "======================================"
echo " INSTALLATION DES DÉPENDANCES PYTHON"
echo "======================================"

# Vérification de Python
if ! command -v python3 &> /dev/null
then
    echo "Erreur : Python3 n'est pas installé."
    exit 1
fi

echo "Python détecté :"
python3 --version

# Vérification de pip
if ! command -v pip3 &> /dev/null
then
    echo "Erreur : pip3 n'est pas installé."
    exit 1
fi

echo "pip détecté :"
pip3 --version

# Mise à jour de pip
python3 -m pip install --upgrade pip

# Installation des dépendances du projet
pip3 install -r requirements.txt

echo "======================================"
echo " DÉPENDANCES INSTALLÉES AVEC SUCCÈS"
echo "======================================"
