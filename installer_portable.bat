@echo off
echo ======================================================
echo    Installation portable de Gestion Markaz
echo ======================================================
echo.
echo Cette procedure va preparer une version portable de l'application
echo qui pourra etre executee depuis une cle USB sans installation.
echo.
echo Veuillez vous assurer d'avoir une connexion Internet active.
echo.
pause

REM Créer le dossier portable s'il n'existe pas
if not exist "portable" mkdir portable
cd portable

REM Télécharger Python embeddable si nécessaire
if not exist "python-3.10.0-embed-amd64.zip" (
    echo Telechargement de Python portable...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-amd64.zip' -OutFile 'python-3.10.0-embed-amd64.zip'"
    echo Extraction de Python portable...
    powershell -Command "Expand-Archive -Path 'python-3.10.0-embed-amd64.zip' -DestinationPath 'python' -Force"
)

REM Télécharger pip si nécessaire
if not exist "python\Scripts\pip.exe" (
    echo Telechargement et installation de pip...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
    python\python.exe get-pip.py
    
    REM Modifier le fichier python310._pth pour activer site-packages
    echo import site >> python\python310._pth
)

REM Installer les dépendances
echo Installation des dependances...
python\python.exe -m pip install -r ..\requirements.txt

REM Créer le script de lancement portable
echo @echo off > lancer_markaz.bat
echo echo ====================================================== >> lancer_markaz.bat
echo echo    Application Gestion Markaz - Version Portable >> lancer_markaz.bat
echo echo ====================================================== >> lancer_markaz.bat
echo echo. >> lancer_markaz.bat
echo echo L'application sera accessible a l'adresse: http://127.0.0.1:8000/ >> lancer_markaz.bat
echo echo. >> lancer_markaz.bat
echo echo Pour arreter le serveur, fermez cette fenetre ou appuyez sur CTRL+C >> lancer_markaz.bat
echo echo. >> lancer_markaz.bat
echo cd .. >> lancer_markaz.bat
echo portable\python\python.exe manage.py runserver >> lancer_markaz.bat
echo pause >> lancer_markaz.bat

REM Copier le script de lancement à la racine
copy lancer_markaz.bat ..\lancer_markaz_portable.bat > nul

cd ..

echo.
echo ======================================================
echo    Installation terminee avec succes!
echo ======================================================
echo.
echo Pour lancer l'application portable:
echo 1. Double-cliquez sur "lancer_markaz_portable.bat"
echo 2. Accedez a l'application via http://127.0.0.1:8000/
echo.
echo Vous pouvez maintenant copier tout le dossier sur une cle USB
echo et l'utiliser sur n'importe quel ordinateur Windows sans
echo avoir a installer Python.
echo.
pause
