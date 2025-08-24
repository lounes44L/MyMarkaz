#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def check_file_for_null_bytes(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        null_positions = [i for i, byte in enumerate(content) if byte == 0]
        return bool(null_positions), null_positions
    except Exception as e:
        print(f"Erreur lors de la lecture de {file_path}: {e}")
        return False, []

def main():
    directory = "."
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    
    print(f"Scan du répertoire: {directory}")
    
    corrupted_files = []
    
    for root, dirs, files in os.walk(directory):
        # Exclure certains répertoires
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                has_null_bytes, positions = check_file_for_null_bytes(file_path)
                
                if has_null_bytes:
                    corrupted_files.append({
                        'path': file_path,
                        'positions': positions,
                        'count': len(positions)
                    })
    
    if not corrupted_files:
        print("Aucun fichier contenant des octets nuls n'a été trouvé.")
    else:
        print(f"Fichiers contenant des octets nuls ({len(corrupted_files)}):")
        for i, file_info in enumerate(corrupted_files, 1):
            print(f"{i}. {file_info['path']} - {file_info['count']} octet(s) nul(s)")

if __name__ == "__main__":
    main()
