@echo off
REM Script pour exécuter la sauvegarde automatique
REM À configurer dans le Planificateur de tâches Windows

echo Démarrage de la sauvegarde automatique - %date% %time%

REM Chemin vers Python (ajustez si nécessaire)
set PYTHON_PATH=python

REM Chemin vers le script de sauvegarde
set SCRIPT_PATH=%~dp0backup_database.py

REM Exécution du script de sauvegarde
cd %~dp0..
%PYTHON_PATH% %SCRIPT_PATH%

echo Sauvegarde terminée - %date% %time%
