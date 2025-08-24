@echo off
echo ======================================================
echo    Lancement de l'application Gestion Markaz
echo ======================================================
echo.

REM Vérifier si Python est installé
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python n'est pas installe sur cet ordinateur.
    echo Veuillez installer Python 3.8 ou superieur pour utiliser cette application.
    echo Vous pouvez le telecharger depuis https://www.python.org/downloads/
    pause
    exit /b
)

REM Vérifier si les dépendances sont installées
echo Verification des dependances...
python -m pip install -r requirements.txt

REM Lancer le serveur Django
echo.
echo Demarrage du serveur...
echo.
echo L'application sera accessible a l'adresse: http://127.0.0.1:8000/
echo.
echo Pour arreter le serveur, fermez cette fenetre ou appuyez sur CTRL+C
echo.
python manage.py runserver

pause
