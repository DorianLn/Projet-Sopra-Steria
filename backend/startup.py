#!/usr/bin/env python3
"""
Script de démarrage complet pour le projet avec Mistral.
Vérifie les dépendances, Ollama, et lance l'API.
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProjectStartup:
    """Gère le démarrage du projet."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = Path(__file__).parent
        
    def print_header(self, text: str):
        """Affiche un en-tête."""
        logger.info("\n" + "=" * 60)
        logger.info(text.center(60))
        logger.info("=" * 60 + "\n")
    
    def check_python_version(self) -> bool:
        """Vérifie la version Python."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            logger.info(f"✓ Python {version.major}.{version.minor} détecté")
            return True
        else:
            logger.error(f"✗ Python 3.8+ requis (détecté: {version.major}.{version.minor})")
            return False
    
    def check_venv(self) -> bool:
        """Vérifie l'environment virtuel."""
        venv_path = self.project_root / "venv"
        
        if not venv_path.exists():
            logger.warning(f"✗ Environment virtuel non trouvé à {venv_path}")
            logger.info("Créez-le avec: python -m venv venv")
            return False
        
        logger.info(f"✓ Environment virtuel trouvé")
        return True
    
    def check_dependencies(self) -> bool:
        """Vérifie les dépendances Python."""
        requirements = self.backend_dir / "requirements.txt"
        
        if not requirements.exists():
            logger.warning(f"✗ requirements.txt non trouvé")
            return False
        
        logger.info(f"✓ requirements.txt trouvé")
        
        # Vérifier les imports critiques
        critical_modules = [
            'flask',
            'flask_cors',
            'docx',
            'spacy',
            'transformers'
        ]
        
        missing = []
        for module in critical_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            logger.warning(f"✗ Modules manquants: {', '.join(missing)}")
            logger.info("Installez avec: pip install -r requirements.txt")
            return False
        
        logger.info("✓ Dépendances Python OK")
        return True
    
    def check_ollama(self) -> bool:
        """Vérifie Ollama."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✓ Ollama détecté: {result.stdout.strip()}")
                return True
        except:
            pass
        
        logger.warning("✗ Ollama non trouvé")
        logger.info("Installez depuis: https://ollama.ai/download")
        return False
    
    def check_ollama_running(self) -> bool:
        """Vérifie si Ollama est lancé."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✓ Ollama en cours d'exécution")
                return True
        except:
            pass
        
        logger.warning("✗ Ollama n'est pas lancé")
        logger.info("Lancez: ollama serve (dans un autre terminal)")
        return False
    
    def check_mistral(self) -> bool:
        """Vérifie si Mistral est téléchargé."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "mistral" in result.stdout.lower():
                logger.info("✓ Mistral téléchargé")
                return True
        except:
            pass
        
        logger.warning("✗ Mistral non trouvé")
        logger.info("Téléchargez: ollama pull mistral")
        return False
    
    def verify_directories(self) -> bool:
        """Vérifie les répertoires nécessaires."""
        required_dirs = [
            self.backend_dir / "data" / "input",
            self.backend_dir / "data" / "output",
            self.backend_dir / "extractors",
            self.backend_dir / "generators",
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                logger.warning(f"✗ Répertoire manquant: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"  Créé: {dir_path}")
        
        logger.info("✓ Répertoires vérifiés")
        return True
    
    def startup_checks(self) -> dict:
        """Exécute tous les tests de démarrage."""
        self.print_header("Vérifications de démarrage")
        
        checks = {
            "Python": self.check_python_version(),
            "Environment virtuel": self.check_venv(),
            "Dépendances Python": self.check_dependencies(),
            "Répertoires": self.verify_directories(),
            "Ollama installé": self.check_ollama(),
            "Ollama lancé": self.check_ollama_running(),
            "Mistral téléchargé": self.check_mistral(),
        }
        
        return checks
    
    def print_summary(self, checks: dict):
        """Affiche un résumé des vérifications."""
        self.print_header("Résumé")
        
        ok_count = sum(1 for v in checks.values() if v)
        total = len(checks)
        
        for check_name, status in checks.items():
            symbol = "✓" if status else "✗"
            logger.info(f"  {symbol} {check_name}")
        
        logger.info(f"\nRésultat: {ok_count}/{total} vérifications OK")
        
        # Recommandations
        if not checks.get("Ollama lancé"):
            logger.warning("\n⚠️  Ollama n'est pas lancé!")
            logger.info("Ouvrez un nouveau terminal et exécutez: ollama serve")
            logger.info("Puis relancez ce script.")
        
        if not checks.get("Mistral téléchargé"):
            logger.warning("\n⚠️  Mistral n'est pas téléchargé!")
            logger.info("Exécutez: ollama pull mistral")
        
        if not checks.get("Dépendances Python"):
            logger.warning("\n⚠️  Dépendances Python manquantes!")
            logger.info("Exécutez: pip install -r requirements.txt")
    
    def start_api(self):
        """Lance l'API Flask."""
        self.print_header("Démarrage de l'API Flask")
        
        os.chdir(str(self.backend_dir))
        
        logger.info("Lancement de api.py...")
        logger.info("L'API sera disponible sur: http://localhost:5000")
        logger.info("Appuyez sur Ctrl+C pour arrêter")
        logger.info("")
        
        try:
            subprocess.run(["python", "api.py"])
        except KeyboardInterrupt:
            logger.info("\n\nAPI arrêtée")
        except Exception as e:
            logger.error(f"Erreur lors du lancement de l'API: {e}")
    
    def run(self, skip_checks=False):
        """Lance le démarrage complet."""
        
        if not skip_checks:
            checks = self.startup_checks()
            self.print_summary(checks)
            
            critical_checks = [
                "Python",
                "Dépendances Python",
                "Répertoires",
            ]
            
            if not all(checks.get(c) for c in critical_checks):
                logger.error("\n❌ Certaines vérifications critiques ont échoué")
                logger.info("Veuillez corriger les problèmes et réessayer")
                return False
            
            if not checks.get("Ollama lancé") or not checks.get("Mistral téléchargé"):
                logger.warning("\n⚠️  Mistral n'est pas complètement configuré")
                response = input("\nContinuer malgré tout? (o/n): ").strip().lower()
                if response != 'o' and response != 'yes':
                    logger.info("Annulation")
                    return False
        
        # Démarrer l'API
        self.start_api()
        return True


def main():
    """Point d'entrée."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Démarrage du projet Sopra avec Mistral"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Ignorer les vérifications de démarrage"
    )
    
    args = parser.parse_args()
    
    startup = ProjectStartup()
    
    try:
        success = startup.run(skip_checks=args.skip_checks)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\nAnnulé par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
