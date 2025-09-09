@echo off
setlocal enabledelayedexpansion

echo Nettoyage des fichiers Python dans le projet Django...
echo.

set "PROJECT_DIR=%~dp0.."
set "TOTAL_FILES=0"
set "CLEANED_FILES=0"

echo Repertoire du projet: %PROJECT_DIR%
echo.

rem Trouver tous les fichiers Python
for /r "%PROJECT_DIR%" %%F in (*.py) do (
    set /a TOTAL_FILES+=1
    
    echo Verification du fichier: %%F
    
    rem Creer un fichier temporaire
    set "TEMP_FILE=%%F.tmp"
    
    rem Verifier et nettoyer le fichier
    type "%%F" > "!TEMP_FILE!"
    
    fc /b "%%F" "!TEMP_FILE!" > nul
    if errorlevel 1 (
        echo Octets nuls trouves dans: %%F
        copy "%%F" "%%F.bak" > nul
        copy "!TEMP_FILE!" "%%F" > nul
        echo Fichier nettoye: %%F (sauvegarde creee: %%F.bak)
        set /a CLEANED_FILES+=1
    ) else (
        echo Pas d'octets nuls dans: %%F
    )
    
    rem Supprimer le fichier temporaire
    del "!TEMP_FILE!" > nul
)

echo.
echo Resume:
echo - Fichiers Python analyses: %TOTAL_FILES%
echo - Fichiers nettoyes: %CLEANED_FILES%

if %CLEANED_FILES% gtr 0 (
    echo.
    echo Des octets nuls ont ete supprimes. Verifiez que votre application fonctionne correctement.
) else (
    echo.
    echo Aucun octet nul n'a ete trouve dans les fichiers Python.
)

endlocal
