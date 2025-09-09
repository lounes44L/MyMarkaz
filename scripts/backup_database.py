#!/usr/bin/env python
"""
Script de sauvegarde automatique pour l'application Gestion_Markaz_Django
Ce script sauvegarde la base de données SQLite et les fichiers média importants
"""

import os
import sys
import shutil
import datetime
import zipfile
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backup_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Chemin du projet (le répertoire parent du script)
BASE_DIR = Path(__file__).resolve().parent.parent

# Répertoire où stocker les sauvegardes
BACKUP_DIR = BASE_DIR / "backups"

# Nombre de jours pendant lesquels conserver les sauvegardes
RETENTION_DAYS = 30

def ensure_backup_dir():
    """Crée le répertoire de sauvegarde s'il n'existe pas"""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)
        logging.info(f"Répertoire de sauvegarde créé: {BACKUP_DIR}")

def clean_old_backups():
    """Supprime les sauvegardes plus anciennes que RETENTION_DAYS"""
    now = datetime.datetime.now()
    count = 0
    
    for backup_file in BACKUP_DIR.glob("*.zip"):
        creation_time = datetime.datetime.fromtimestamp(backup_file.stat().st_ctime)
        age_days = (now - creation_time).days
        
        if age_days > RETENTION_DAYS:
            backup_file.unlink()
            count += 1
            logging.info(f"Sauvegarde supprimée (âge: {age_days} jours): {backup_file.name}")
    
    if count > 0:
        logging.info(f"{count} anciennes sauvegardes supprimées")

def create_backup():
    """Crée une sauvegarde de la base de données et des fichiers média"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"markaz_backup_{timestamp}.zip"
    backup_path = BACKUP_DIR / backup_filename
    
    # Fichiers à sauvegarder
    db_file = BASE_DIR / "db.sqlite3"
    media_dirs = [
        BASE_DIR / "cours_partages",
        # Ajoutez d'autres répertoires de médias si nécessaire
    ]
    
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Sauvegarde de la base de données
            if db_file.exists():
                zipf.write(db_file, arcname=db_file.name)
                logging.info(f"Base de données sauvegardée: {db_file}")
            else:
                logging.error(f"Fichier de base de données non trouvé: {db_file}")
            
            # Sauvegarde des répertoires média
            for media_dir in media_dirs:
                if media_dir.exists() and media_dir.is_dir():
                    for file_path in media_dir.glob('**/*'):
                        if file_path.is_file():
                            # Chemin relatif dans l'archive
                            arcname = str(file_path.relative_to(BASE_DIR))
                            zipf.write(file_path, arcname=arcname)
                    logging.info(f"Répertoire média sauvegardé: {media_dir}")
                else:
                    logging.warning(f"Répertoire média non trouvé: {media_dir}")
        
        logging.info(f"Sauvegarde créée avec succès: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Erreur lors de la création de la sauvegarde: {e}")
        return False

def main():
    """Fonction principale"""
    logging.info("Démarrage de la sauvegarde...")
    
    ensure_backup_dir()
    clean_old_backups()
    success = create_backup()
    
    if success:
        logging.info("Sauvegarde terminée avec succès")
    else:
        logging.error("La sauvegarde a échoué")

if __name__ == "__main__":
    main()
