#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CV Sopra Steria - Launcher
Installe les dépendances et lance le backend + frontend
"""

import os
import sys
import subprocess
import time
import webbrowser
import ctypes
import socket
import threading
from pathlib import Path

# Configuration
DOMAIN = "cv.soprasteria.com"
BACKEND_PORT = 5000
FRONTEND_PORT = 5173
APP_URL = f"http://{DOMAIN}:{FRONTEND_PORT}"

def is_admin():
    """Vérifie si le script est exécuté en tant qu'administrateur"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Relance le script en tant qu'administrateur"""
    if sys.platform == 'win32':
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
            sys.exit(0)
        except Exception as e:
            print(f"Erreur lors de l'élévation des privilèges: {e}")
            return False
    return False

def get_base_path():
    """Retourne le chemin de base du projet"""
    if getattr(sys, 'frozen', False):
        # Exécution depuis l'exécutable PyInstaller
        return Path(sys.executable).parent
    else:
        # Exécution depuis le script Python
        return Path(__file__).parent

def check_hosts_entry():
    """Vérifie si l'entrée existe dans le fichier hosts"""
    hosts_path = Path(r"C:\Windows\System32\drivers\etc\hosts")
    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return DOMAIN in content
    except:
        return False

def add_hosts_entry():
    """Ajoute l'entrée cv.soprasteria.com dans le fichier hosts"""
    hosts_path = Path(r"C:\Windows\System32\drivers\etc\hosts")
    
    if check_hosts_entry():
        print(f"✓ {DOMAIN} déjà configuré dans hosts")
        return True
    
    try:
        with open(hosts_path, 'a', encoding='utf-8') as f:
            f.write(f"\n# CV Sopra Steria - Application locale\n")
            f.write(f"127.0.0.1       {DOMAIN}\n")
        print(f"✓ {DOMAIN} ajouté au fichier hosts")
        return True
    except PermissionError:
        print(f"⚠ Droits administrateur requis pour modifier le fichier hosts")
        return False
    except Exception as e:
        print(f"✗ Erreur lors de la modification du fichier hosts: {e}")
        return False

def check_python():
    """Vérifie que Python est installé"""
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        print(f"✓ Python trouvé: {result.stdout.strip()}")
        return True
    except:
        print("✗ Python non trouvé")
        return False

def check_node():
    """Vérifie que Node.js est installé"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        print(f"✓ Node.js trouvé: {result.stdout.strip()}")
        return True
    except:
        print("✗ Node.js non trouvé. Veuillez installer Node.js: https://nodejs.org/")
        return False

def check_npm():
    """Vérifie que npm est installé"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
        print(f"✓ npm trouvé: v{result.stdout.strip()}")
        return True
    except:
        print("✗ npm non trouvé")
        return False

def setup_venv(base_path):
    """Crée et configure l'environnement virtuel Python"""
    venv_path = base_path / 'venv'
    backend_path = base_path / 'backend'
    requirements_path = backend_path / 'requirements.txt'
    
    # Créer le venv si nécessaire
    if not venv_path.exists():
        print("\n📦 Création de l'environnement virtuel Python...")
        subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
        print("✓ Environnement virtuel créé")
    else:
        print("✓ Environnement virtuel existant")
    
    # Déterminer le chemin Python dans le venv
    if sys.platform == 'win32':
        python_venv = venv_path / 'Scripts' / 'python.exe'
        pip_venv = venv_path / 'Scripts' / 'pip.exe'
    else:
        python_venv = venv_path / 'bin' / 'python'
        pip_venv = venv_path / 'bin' / 'pip'
    
    # Installer les dépendances Python
    marker_file = venv_path / '.deps_installed'
    if not marker_file.exists():
        print("\n📦 Installation des dépendances Python...")
        # Utiliser python -m pip au lieu de pip directement
        subprocess.run([str(python_venv), '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([str(python_venv), '-m', 'pip', 'install', '-r', str(requirements_path)], check=True)
        
        # Télécharger le modèle spaCy français
        print("\n📦 Téléchargement du modèle spaCy français...")
        subprocess.run([str(python_venv), '-m', 'spacy', 'download', 'fr_core_news_md'], check=True)
        
        # Marquer comme installé
        marker_file.touch()
        print("✓ Dépendances Python installées")
    else:
        print("✓ Dépendances Python déjà installées")
    
    return python_venv

def setup_frontend(base_path):
    """Installe les dépendances npm du frontend"""
    frontend_path = base_path / 'frontend'
    node_modules = frontend_path / 'node_modules'
    
    if not node_modules.exists():
        print("\n📦 Installation des dépendances npm...")
        subprocess.run(['npm', 'install'], cwd=str(frontend_path), shell=True, check=True)
        print("✓ Dépendances npm installées")
    else:
        print("✓ Dépendances npm déjà installées")
    
    return True

def is_port_in_use(port):
    """Vérifie si un port est déjà utilisé"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def wait_for_server(port, timeout=60):
    """Attend qu'un serveur soit disponible sur un port"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.5)
    return False

def start_backend(base_path, python_venv):
    """Démarre le backend Flask"""
    backend_path = base_path / 'backend'
    
    if is_port_in_use(BACKEND_PORT):
        print(f"⚠ Le port {BACKEND_PORT} est déjà utilisé (backend déjà lancé?)")
        return None
    
    print(f"\n🚀 Démarrage du backend sur le port {BACKEND_PORT}...")
    
    env = os.environ.copy()
    env['FLASK_APP'] = 'api.py'
    env['FLASK_ENV'] = 'development'
    
    process = subprocess.Popen(
        [str(python_venv), 'api.py'],
        cwd=str(backend_path),
        env=env,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    if wait_for_server(BACKEND_PORT, timeout=30):
        print(f"✓ Backend démarré sur http://localhost:{BACKEND_PORT}")
    else:
        print(f"⚠ Timeout: le backend n'a pas démarré dans les temps")
    
    return process

def start_frontend(base_path):
    """Démarre le frontend Vite avec le domaine personnalisé"""
    frontend_path = base_path / 'frontend'
    
    if is_port_in_use(FRONTEND_PORT):
        print(f"⚠ Le port {FRONTEND_PORT} est déjà utilisé (frontend déjà lancé?)")
        return None
    
    print(f"\n🚀 Démarrage du frontend sur {APP_URL}...")
    
    process = subprocess.Popen(
        ['npm', 'run', 'dev', '--', '--host', DOMAIN, '--port', str(FRONTEND_PORT)],
        cwd=str(frontend_path),
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    if wait_for_server(FRONTEND_PORT, timeout=60):
        print(f"✓ Frontend démarré sur {APP_URL}")
    else:
        print(f"⚠ Timeout: le frontend n'a pas démarré dans les temps")
    
    return process

def open_browser():
    """Ouvre le navigateur après un délai"""
    time.sleep(3)
    webbrowser.open(APP_URL)
    print(f"\n🌐 Ouverture du navigateur: {APP_URL}")

def print_banner():
    """Affiche la bannière de démarrage"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ██████╗██╗   ██╗    ███████╗ ██████╗ ██████╗ ██████╗     ║
║    ██╔════╝██║   ██║    ██╔════╝██╔═══██╗██╔══██╗██╔══██╗    ║
║    ██║     ██║   ██║    ███████╗██║   ██║██████╔╝██████╔╝    ║
║    ██║     ╚██╗ ██╔╝    ╚════██║██║   ██║██╔═══╝ ██╔══██╗    ║
║    ╚██████╗ ╚████╔╝     ███████║╚██████╔╝██║     ██║  ██║    ║
║     ╚═════╝  ╚═══╝      ╚══════╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝    ║
║                                                              ║
║              CV Normalizer - Sopra Steria                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    global APP_URL
    
    print_banner()
    
    base_path = get_base_path()
    print(f"📂 Répertoire du projet: {base_path}\n")
    
    # Vérifier les prérequis d'abord
    print("🔍 Vérification des prérequis...\n")
    
    if not check_python():
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    if not check_node() or not check_npm():
        print("\n❌ Node.js et npm sont requis pour le frontend.")
        print("   Téléchargez-les sur: https://nodejs.org/")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    # Vérifier si le domaine est déjà configuré
    print("\n🔧 Configuration du domaine personnalisé...")
    use_custom_domain = False
    
    if check_hosts_entry():
        print(f"✓ {DOMAIN} déjà configuré dans hosts")
        use_custom_domain = True
    elif is_admin():
        # On a les droits admin, on peut configurer
        if add_hosts_entry():
            use_custom_domain = True
    else:
        # Pas admin et domaine pas configuré
        print(f"⚠ Le domaine {DOMAIN} n'est pas configuré.")
        print(f"  Pour l'activer, exécutez setup_domain.bat en administrateur.")
        print(f"  L'application va démarrer sur localhost pour l'instant.\n")
    
    # Mettre à jour l'URL selon la configuration
    if use_custom_domain:
        APP_URL = f"http://{DOMAIN}:{FRONTEND_PORT}"
    else:
        APP_URL = f"http://localhost:{FRONTEND_PORT}"
    
    # Configuration de l'environnement Python
    print("\n🔧 Configuration de l'environnement...")
    python_venv = setup_venv(base_path)
    
    # Installation des dépendances frontend
    setup_frontend(base_path)
    
    # Démarrer les serveurs
    backend_process = start_backend(base_path, python_venv)
    frontend_process = start_frontend(base_path)
    
    # Ouvrir le navigateur dans un thread séparé
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("\n" + "="*60)
    print(f"✅ Application démarrée!")
    print(f"   🌐 URL: {APP_URL}")
    print(f"   📡 Backend API: http://localhost:{BACKEND_PORT}")
    print("="*60)
    print("\n⚠ Gardez cette fenêtre ouverte pour maintenir les serveurs actifs.")
    print("   Appuyez sur Ctrl+C pour arrêter l'application.\n")
    
    try:
        # Maintenir le script en vie
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de l'application...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✓ Application arrêtée.")

if __name__ == '__main__':
    main()
