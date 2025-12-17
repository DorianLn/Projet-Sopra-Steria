#!/usr/bin/env python3
"""
Script de setup pour Ollama + Mistral 7B.
Automatise l'installation et la configuration.
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
from typing import Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaSetup:
    """Gère l'installation et la configuration d'Ollama."""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_mac = self.system == "Darwin"
        self.is_linux = self.system == "Linux"
    
    def check_ollama_installed(self) -> bool:
        """Vérifie si Ollama est installé."""
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
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.warning("✗ Ollama non trouvé")
        return False
    
    def check_ollama_running(self) -> bool:
        """Vérifie si le service Ollama est en cours d'exécution."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def install_ollama(self) -> bool:
        """
        Guide l'utilisateur pour installer Ollama.
        Returns True si l'installation est réussie.
        """
        logger.info("\n=== Installation d'Ollama ===\n")
        
        if self.is_windows:
            logger.info(
                "Pour Windows:\n"
                "1. Visitez https://ollama.ai/download/windows\n"
                "2. Téléchargez et exécutez l'installer\n"
                "3. Suivez les instructions d'installation\n"
            )
        elif self.is_mac:
            logger.info(
                "Pour macOS:\n"
                "1. Visitez https://ollama.ai/download/mac\n"
                "2. Téléchargez et exécutez l'installer\n"
                "OU via Homebrew:\n"
                "   brew install ollama\n"
            )
        else:  # Linux
            logger.info(
                "Pour Linux:\n"
                "Exécutez:\n"
                "   curl https://ollama.ai/install.sh | sh\n"
            )
        
        input("Appuyez sur Entrée après avoir installé Ollama...")
        
        return self.check_ollama_installed()
    
    def start_ollama_service(self) -> bool:
        """Lance le service Ollama."""
        logger.info("\n=== Démarrage d'Ollama ===\n")
        
        if self.check_ollama_running():
            logger.info("✓ Ollama est déjà en cours d'exécution")
            return True
        
        logger.info(
            "Ollama n'est pas en cours d'exécution.\n"
            "Veuillez ouvrir un nouveau terminal et exécuter:\n"
            "   ollama serve\n"
        )
        
        input("Appuyez sur Entrée une fois que Ollama est lancé...")
        
        return self.check_ollama_running()
    
    def pull_mistral_model(self) -> bool:
        """Télécharge le modèle Mistral."""
        logger.info("\n=== Téléchargement du modèle Mistral ===\n")
        
        try:
            logger.info("Téléchargement de mistral (cela peut prendre quelques minutes)...")
            result = subprocess.run(
                ["ollama", "pull", "mistral"],
                timeout=3600  # 1 heure de timeout
            )
            
            if result.returncode == 0:
                logger.info("✓ Mistral téléchargé avec succès")
                return True
            else:
                logger.error("✗ Erreur lors du téléchargement de Mistral")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("✗ Le téléchargement a expiré (timeout)")
            return False
        except FileNotFoundError:
            logger.error("✗ Ollama n'a pas pu être exécuté")
            return False
    
    def verify_setup(self) -> Tuple[bool, str]:
        """Vérifie que tout est bien configuré."""
        logger.info("\n=== Vérification du setup ===\n")
        
        checks = []
        
        # Vérifier Ollama
        if self.check_ollama_installed():
            checks.append("✓ Ollama installé")
        else:
            checks.append("✗ Ollama non installé")
        
        # Vérifier que Ollama tourne
        if self.check_ollama_running():
            checks.append("✓ Ollama en cours d'exécution")
        else:
            checks.append("✗ Ollama n'est pas lancé")
        
        # Vérifier Mistral
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "mistral" in result.stdout:
                checks.append("✓ Mistral téléchargé")
            else:
                checks.append("✗ Mistral non trouvé")
        except:
            checks.append("✗ Impossible de vérifier Mistral")
        
        for check in checks:
            logger.info(check)
        
        all_ok = all(check.startswith("✓") for check in checks)
        
        return all_ok, "\n".join(checks)
    
    def full_setup(self) -> bool:
        """Lance le setup complet."""
        logger.info("=" * 50)
        logger.info("Configuration de Mistral 7B avec Ollama")
        logger.info("=" * 50)
        
        # Étape 1: Vérifier/installer Ollama
        if not self.check_ollama_installed():
            if not self.install_ollama():
                logger.error("Installation d'Ollama échouée")
                return False
        
        # Étape 2: Démarrer Ollama
        if not self.start_ollama_service():
            logger.error("Ollama n'a pas pu être lancé")
            return False
        
        # Étape 3: Télécharger Mistral
        if not self.pull_mistral_model():
            logger.error("Téléchargement de Mistral échoué")
            return False
        
        # Étape 4: Vérifier
        success, summary = self.verify_setup()
        
        logger.info("\n" + "=" * 50)
        if success:
            logger.info("✓ Setup réussi! Mistral est prêt à l'emploi")
        else:
            logger.error("✗ Certaines vérifications ont échoué")
        logger.info("=" * 50)
        
        return success


def main():
    """Point d'entrée principal."""
    setup = OllamaSetup()
    
    try:
        success = setup.full_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\nInstallation annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
