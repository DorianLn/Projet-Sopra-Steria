@echo off
REM Script pour gérer Ollama et Mistral sur Windows

setlocal enabledelayedexpansion

echo.
echo ========================================
echo GESTIONNAIRE MISTRAL - Projet Sopra
echo ========================================
echo.

:menu
echo Options:
echo 1. Vérifier l'installation Ollama
echo 2. Lancer Ollama (ollama serve)
echo 3. Télécharger Mistral (ollama pull mistral)
echo 4. Vérifier le setup complet
echo 5. Lancer un test d'analyse CV
echo 6. Ouvrir l'explorateur sur le dossier du projet
echo 7. Quitter
echo.

set /p choice="Entrez votre choix (1-7): "

if "%choice%"=="1" goto check_install
if "%choice%"=="2" goto run_ollama
if "%choice%"=="3" goto pull_mistral
if "%choice%"=="4" goto verify_setup
if "%choice%"=="5" goto test_analysis
if "%choice%"=="6" goto open_explorer
if "%choice%"=="7" goto end
echo Choix invalide
goto menu

:check_install
echo.
echo Vérification d'Ollama...
where ollama >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Ollama est installé
    ollama --version
) else (
    echo ✗ Ollama n'est pas trouvé
    echo Installez depuis: https://ollama.ai/download/windows
)
echo.
pause
goto menu

:run_ollama
echo.
echo Lancement d'Ollama (ollama serve)...
echo Ne fermez pas cette fenêtre!
echo.
ollama serve
echo.
pause
goto menu

:pull_mistral
echo.
echo Téléchargement de Mistral...
echo Cela peut prendre plusieurs minutes (~4 GB)
echo.
ollama pull mistral
echo.
echo ✓ Téléchargement terminé
pause
goto menu

:verify_setup
echo.
echo Vérification du setup complet...
echo.
python "%~dp0setup_ollama.py"
echo.
pause
goto menu

:test_analysis
echo.
echo Lancement du test d'analyse CV...
echo.
python "%~dp0examples_mistral.py"
echo.
pause
goto menu

:open_explorer
echo.
echo Ouverture du dossier du projet...
start explorer "%~dp0"
goto menu

:end
echo.
echo Bye!
echo.
exit /b 0
