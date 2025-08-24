#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour nettoyer tous les fichiers Python du projet en supprimant les octets nuls
et en corrigeant les problèmes d'encodage.
"""

import os
import sys
import re
import codecs
import shutil
from pathlib import Path
import argparse

def detect_encoding(file_path):
    """Détecte l'encodage d'un fichier."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as f:
                f.read()
                return encoding
        except UnicodeDecodeError:
            continue
    
    return 'utf-8'  # Par défaut

def clean_file(file_path, backup=True, verbose=False):
    """
    Nettoie un fichier Python en supprimant les octets nuls et en corrigeant l'encodage.
    
    Args:
        file_path: Chemin du fichier à nettoyer
        backup: Si True, crée une copie de sauvegarde avant modification
        verbose: Si True, affiche des informations détaillées
    
    Returns:
        tuple: (modifié, contient_null_bytes, message)
    """
    if verbose:
        print(f"Traitement du fichier: {file_path}")
    
    # Vérifier si le fichier existe
    if not os.path.isfile(file_path):
        return False, False, f"Le fichier {file_path} n'existe pas"
    
    # Lire le contenu binaire du fichier
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Vérifier la présence d'octets nuls
    contains_null_bytes = b'\x00' in content
    
    if not contains_null_bytes:
        # Vérifier si le fichier peut être lu en UTF-8 sans erreur
        try:
            content.decode('utf-8')
            if verbose:
                print(f"✓ {file_path} - Pas d'octets nuls, encodage UTF-8 valide")
            return False, False, "Pas de problème détecté"
        except UnicodeDecodeError:
            pass  # Continuer avec le nettoyage si l'encodage pose problème
    
    # Créer une sauvegarde si demandé
    if backup:
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        if verbose:
            print(f"✓ Sauvegarde créée: {backup_path}")
    
    # Supprimer les octets nuls
    cleaned_content = content.replace(b'\x00', b'')
    
    # Détecter l'encodage probable et convertir en UTF-8
    try:
        # Essayer de décoder avec l'encodage détecté
        encoding = detect_encoding(file_path)
        if encoding != 'utf-8':
            text = cleaned_content.decode(encoding, errors='replace')
            cleaned_content = text.encode('utf-8')
    except Exception as e:
        # En cas d'erreur, utiliser 'replace' pour remplacer les caractères problématiques
        text = cleaned_content.decode('utf-8', errors='replace')
        cleaned_content = text.encode('utf-8')
    
    # Écrire le contenu nettoyé
    with open(file_path, 'wb') as f:
        f.write(cleaned_content)
    
    message = []
    if contains_null_bytes:
        message.append("Octets nuls supprimés")
    message.append(f"Encodage corrigé en UTF-8")
    
    if verbose:
        print(f"✓ {file_path} - {', '.join(message)}")
    
    return True, contains_null_bytes, ', '.join(message)

def process_directory(directory, extensions=['.py'], backup=True, verbose=False, recursive=True):
    """
    Traite tous les fichiers avec les extensions spécifiées dans un répertoire.
    
    Args:
        directory: Répertoire à traiter
        extensions: Liste des extensions de fichiers à traiter
        backup: Si True, crée des sauvegardes avant modification
        verbose: Si True, affiche des informations détaillées
        recursive: Si True, traite également les sous-répertoires
    
    Returns:
        dict: Statistiques sur les fichiers traités
    """
    stats = {
        'total': 0,
        'modified': 0,
        'with_null_bytes': 0,
        'errors': 0
    }
    
    if verbose:
        print(f"\nTraitement du répertoire: {directory}")
    
    for root, dirs, files in os.walk(directory):
        # Ignorer les dossiers .git et __pycache__
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        
        # Arrêter la récursion si non demandée
        if not recursive and root != directory:
            dirs.clear()  # Vide la liste des sous-répertoires pour arrêter la récursion
            continue
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                stats['total'] += 1
                
                try:
                    modified, has_null_bytes, message = clean_file(file_path, backup, verbose)
                    
                    if modified:
                        stats['modified'] += 1
                    if has_null_bytes:
                        stats['with_null_bytes'] += 1
                        
                except Exception as e:
                    stats['errors'] += 1
                    if verbose:
                        print(f"❌ Erreur lors du traitement de {file_path}: {str(e)}")
    
    return stats

def main():
    parser = argparse.ArgumentParser(description="Nettoie les fichiers Python en supprimant les octets nuls et en corrigeant l'encodage")
    parser.add_argument('directory', nargs='?', default='.', help="Répertoire à traiter (par défaut: répertoire courant)")
    parser.add_argument('-e', '--extensions', nargs='+', default=['.py'], help="Extensions de fichiers à traiter (par défaut: .py)")
    parser.add_argument('-r', '--recursive', action='store_true', help="Traiter récursivement les sous-répertoires")
    parser.add_argument('-n', '--no-backup', action='store_true', help="Ne pas créer de sauvegardes")
    parser.add_argument('-v', '--verbose', action='store_true', help="Afficher des informations détaillées")
    
    args = parser.parse_args()
    
    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"Erreur: {directory} n'est pas un répertoire valide")
        sys.exit(1)
    
    print(f"Nettoyage des fichiers {', '.join(args.extensions)} dans {directory}")
    print(f"Mode récursif: {'Oui' if args.recursive else 'Non'}")
    print(f"Création de sauvegardes: {'Non' if args.no_backup else 'Oui'}")
    
    stats = process_directory(
        directory, 
        extensions=args.extensions, 
        backup=not args.no_backup, 
        verbose=args.verbose,
        recursive=args.recursive
    )
    
    print("\nRésultats:")
    print(f"- Fichiers analysés: {stats['total']}")
    print(f"- Fichiers modifiés: {stats['modified']}")
    print(f"- Fichiers avec octets nuls: {stats['with_null_bytes']}")
    print(f"- Erreurs: {stats['errors']}")
    
    if stats['with_null_bytes'] > 0:
        print("\n✅ Des octets nuls ont été supprimés. Vérifiez que votre application fonctionne correctement.")
    
    if stats['errors'] > 0:
        print("\n⚠️ Des erreurs sont survenues pendant le traitement. Vérifiez les messages d'erreur.")

if __name__ == "__main__":
    main()
