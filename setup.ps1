#requires -Version 5.1
param(
    [switch]$InstallOnly
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location $root

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Ensure-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Dépendance manquante : $Name. $Hint"
    }
}

function Ensure-Version([string]$Label, [Version]$Current, [Version]$Minimum) {
    if ($Current -lt $Minimum) {
        throw "$Label détecté ($Current) < version requise ($Minimum)."
    }
}

Write-Step "Vérification des prérequis globaux"
Ensure-Command -Name "python" -Hint "Installez Python 3.10+ : https://www.python.org/downloads/"
$pythonVersion = [Version](& python -c "import sys;print('.'.join(map(str, sys.version_info[:3])))")
Ensure-Version -Label "Python" -Current $pythonVersion -Minimum ([Version]"3.10.0")

$pipInfo = & python -m pip --version
$pipVersion = [Version]($pipInfo.Split()[1])
Ensure-Version -Label "pip" -Current $pipVersion -Minimum ([Version]"23.0.0")

Ensure-Command -Name "node" -Hint "Installez Node.js 18+ : https://nodejs.org/en/download"
$nodeVersion = [Version]((node -v).TrimStart('v'))
Ensure-Version -Label "Node.js" -Current $nodeVersion -Minimum ([Version]"18.0.0")

Ensure-Command -Name "npm" -Hint "npm est fourni avec Node.js 18+."

$backendPath  = Join-Path $root "backend"
$frontendPath = Join-Path $root "frontend"
if (-not (Test-Path $backendPath))  { throw "Dossier backend introuvable : $backendPath" }
if (-not (Test-Path $frontendPath)) { throw "Dossier frontend introuvable : $frontendPath" }

Write-Step "Préparation de l'environnement backend"
$venvPath   = Join-Path $backendPath "venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip    = Join-Path $venvPath "Scripts\pip.exe"

if (-not (Test-Path $venvPath)) {
    Write-Host "Création du venv..."
    python -m venv $venvPath
}

& $venvPip install --upgrade pip setuptools wheel
& $venvPip install -r (Join-Path $backendPath "requirements.txt")

& $venvPython -c "import importlib.util, sys; sys.exit(0) if importlib.util.find_spec('fr_core_news_md') else sys.exit(1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installation du modèle spaCy fr_core_news_md..."
    & $venvPython -m spacy download fr_core_news_md
}

Write-Step "Préparation des dépendances frontend"
$nodeModulesPath = Join-Path $frontendPath "node_modules"
$packageLockPath = Join-Path $frontendPath "package-lock.json"
$shouldInstallFrontend = -not (Test-Path $nodeModulesPath)

if (-not $shouldInstallFrontend -and (Test-Path $packageLockPath)) {
    $shouldInstallFrontend = ([IO.File]::GetLastWriteTime($packageLockPath) -gt [IO.Directory]::GetLastWriteTime($nodeModulesPath))
}

if ($shouldInstallFrontend) {
    Push-Location $frontendPath
    npm install
    Pop-Location
} else {
    Write-Host "node_modules déjà à jour."
}

if ($InstallOnly) {
    Write-Step "Installation terminée (mode --InstallOnly)."
    return
}

Write-Step "Lancement des serveurs (nouvelles consoles persistantes)"
$backendCommand  = "Set-Location `"$backendPath`"; & `"$venvPython`" api.py"
$frontendCommand = "Set-Location `"$frontendPath`"; npm run dev"

Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit","-Command",$backendCommand  | Out-Null
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit","-Command",$frontendCommand | Out-Null

Write-Host ""
Write-Host "Backend : http://localhost:5000"
Write-Host "Frontend : http://localhost:5173"
Write-Host "Les deux processus tournent dans des terminaux séparés." -ForegroundColor Green