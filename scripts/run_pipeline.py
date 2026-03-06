import subprocess
import os
import time

# ==========================================
# LISTE DES SCRIPTS À EXÉCUTER (Dans l'ordre)
# ==========================================
scripts_a_lancer = [
    "niveau_etudes_2022_clean.py",
    "clean_densite_population.py",
    "clean_criminalite.py",
    "clean_population.py",
    "clean_immigration.py",
    "clean_activite_nationalite.py",
    "clean_abstention.py",
    "clean_elections_partis.py",
    "clean_revenus.py",
    "clean_foncier.py",
    "clean_elections_communaute.py"
]

# On s'assure d'être dans le bon dossier (celui du script actuel)
dossier_scripts = os.path.dirname(os.path.abspath(__file__))
os.chdir(dossier_scripts)

print("🚀 Démarrage du pipeline ETL Master...")
print("="*50)

temps_debut_total = time.time()

# Boucle d'exécution
for script in scripts_a_lancer:
    print(f"⏳ En cours : {script} ...")
    temps_debut_script = time.time()
    
    # Lancement du sous-script
    result = subprocess.run(["python", script], capture_output=True, text=True)
    
    temps_fin_script = time.time()
    duree = round(temps_fin_script - temps_debut_script, 2)
    
    # Vérification du succès (Code de retour 0 = Tout va bien)
    if result.returncode == 0:
        print(f"  ✅ Succès ({duree} sec)")
    else:
        print(f"  ❌ ERREUR sur {script} !")
        print("-" * 50)
        print("Détail de l'erreur (Log) :")
        print(result.stderr) # Affiche l'erreur exacte pour t'aider à débugger
        print("-" * 50)
        print("🛑 Arrêt du pipeline. Corrige l'erreur avant de relancer.")
        exit(1) # Stoppe complètement le programme

temps_fin_total = time.time()
duree_totale = round(temps_fin_total - temps_debut_total, 2)

print("="*50)
print(f"🎉 PIPELINE TERMINÉ AVEC SUCCÈS en {duree_totale} secondes !")
print("📁 Tous tes fichiers propres t'attendent dans 'data_clean/'.")