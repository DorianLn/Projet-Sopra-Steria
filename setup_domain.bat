@echo off
net session >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Ce script doit etre execute en tant qu'administrateur!
    echo Clic droit sur le fichier puis Executer en tant qu'administrateur
    pause
    exit /b 1
)

set HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts
set DOMAIN=cv.soprasteria.com

findstr /C:"%DOMAIN%" "%HOSTS_FILE%" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Le domaine %DOMAIN% est deja configure.
    pause
    exit /b 0
)

echo.>> "%HOSTS_FILE%"
echo 127.0.0.1       %DOMAIN%>> "%HOSTS_FILE%"

if errorlevel 1 (
    echo [ERREUR] Impossible de modifier le fichier hosts
    pause
    exit /b 1
)

echo [OK] Domaine %DOMAIN% configure avec succes!
echo Vous pouvez maintenant acceder a l'application via: http://%DOMAIN%:5173
ipconfig /flushdns >nul 2>&1
pause
