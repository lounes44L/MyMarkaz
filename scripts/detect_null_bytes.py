#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour détecter les octets nuls (null bytes) dans les fichiers Python d'un projet Django.
Ce script parcourt récursivement tous les fichiers .py dans le répertoire spécifié
et identifie ceux qui contiennent des octets nuls, qui peuvent causer des erreurs SyntaxError.
"""

import os
import sys
import argparse
from pathlib import Path

def check_file_for_null_bytes(file_path):
    """
    Vérifie si un fichier contient des octets nuls (null bytes).
    
    Args:
        file_path (str): Chemin vers le fichier à vérifier
        
    Returns:
        tuple: (contient_octet_nul, positions) où positions est une liste des positions des octets nuls
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # Recherche des octets nuls (0x00)
        null_positions = [i for i, byte in enumerate(content) if byte == 0]
        
        return bool(null_positions), null_positions
    except Exception as e:
        print(f"Erreur lors de la lecture de {file_path}: {e}")
        return False, []

def scan_directory(directory, extensions=None, exclude_dirs=None):
    """
    Parcourt récursivement un répertoire et vérifie les fichiers pour les octets nuls.
    
    Args:
        directory (str): Répertoire à scanner
        extensions (list): Liste des extensions de fichiers à vérifier (par défaut: ['.py'])
        exclude_dirs (list): Liste des répertoires à exclure
        
    Returns:
        list: Liste des fichiers contenant des octets nuls avec leurs positions
    """
    if extensions is None:
        extensions = ['.py']
    
    if exclude_dirs is None:
        exclude_dirs = ['venv', 'env', '.git', '__pycache__', 'migrations']
    
    corrupted_files = []
    
    for root, dirs, files in os.walk(directory):
        # Exclure les répertoires spécifiés
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                has_null_bytes, positions = check_file_for_null_bytes(file_path)
                
                if has_null_bytes:
                    corrupted_files.append({
                        'path': file_path,
                        'positions': positions,
                        'count': len(positions)
                    })
    
    return corrupted_files

def create_clean_file(file_path, positions):
    """
    Crée une version propre d'un fichier en supprimant les octets nuls.
    
    Args:
        file_path (str): Chemin vers le fichier corrompu
        positions (list): Positions des octets nuls dans le fichier
        
    Returns:
        str: Chemin vers le fichier nettoyé
    """
    try:
        with open(file_path, 'rb') as f:
            content = bytearray(f.read())
        
        # Supprimer les octets nuls
        for pos in sorted(positions, reverse=True):
            del content[pos]
        
        # Créer le nom du fichier nettoyé
        clean_path = f"{file_path}.clean"
        
        # Écrire le contenu nettoyé
        with open(clean_path, 'wb') as f:
            f.write(content)
        
        return clean_path
    except Exception as e:
        print(f"Erreur lors de la création du fichier propre pour {file_path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Détecte les octets nuls dans les fichiers Python.')
    parser.add_argument('directory', nargs='?', default='.', help='Répertoire à scanner (par défaut: répertoire courant)')
    parser.add_argument('--create-clean', action='store_true', help='Créer des versions propres des fichiers corrompus')
    parser.add_argument('--extensions', nargs='+', default=['.py'], help='Extensions de fichiers à vérifier (par défaut: .py)')
    parser.add_argument('--exclude-dirs', nargs='+', default=['venv', 'env', '.git', '__pycache__', 'migrations'], 
                        help='Répertoires à exclure')
    
    args = parser.parse_args()
    
    print(f"Scan du répertoire: {args.directory}")
    print(f"Extensions vérifiées: {', '.join(args.extensions)}")
    print(f"Répertoires exclus: {', '.join(args.exclude_dirs)}")
    print("-" * 80)
    
    corrupted_files = scan_directory(args.directory, args.extensions, args.exclude_dirs)
    
    if not corrupted_files:
        print("Aucun fichier contenant des octets nuls n'a été trouvé.")
        return 0
    
    print(f"Fichiers contenant des octets nuls ({len(corrupted_files)}):")
    for i, file_info in enumerate(corrupted_files, 1):
        print(f"{i}. {file_info['path']} - {file_info['count']} octet(s) nul(s) aux positions: {file_info['positions']}")
    
    if args.create_clean:
        print("\nCréation des versions propres:")
        for file_info in corrupted_files:
            clean_path = create_clean_file(file_info['path'], file_info['positions'])
            if clean_path:
                print(f"Version propre créée: {clean_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
