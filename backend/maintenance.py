#!/usr/bin/env python3
"""
Script de maintenance et d'administration pour Mistral.
Aide à gérer les logs, les caches et les modèles.
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MistralMaintenance:
    """Gère la maintenance de Mistral/Ollama."""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.data_dir = self.backend_dir / "data"
        self.output_dir = self.data_dir / "output"
        self.log_dir = self.backend_dir / "logs"
    
    def print_menu(self):
        """Affiche le menu principal."""
        print("\n" + "=" * 60)
        print("MAINTENANCE MISTRAL / OLLAMA".center(60))
        print("=" * 60 + "\n")
        print("Options:")
        print("1. Afficher les modèles Ollama disponibles")
        print("2. Afficher l'utilisation disque des modèles")
        print("3. Nettoyer les fichiers temporaires")
        print("4. Nettoyer les anciens résultats JSON")
        print("5. Vérifier la santé de Mistral")
        print("6. Relancer Ollama")
        print("7. Télécharger une nouvelle version de Mistral")
        print("8. Supprimer tous les modèles Ollama")
        print("9. Afficher les logs récents")
        print("10. Exporter les résultats")
        print("11. Quitter\n")
    
    def list_ollama_models(self):
        """Liste les modèles Ollama."""
        print("\n=== Modèles Ollama ===\n")
        
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                logger.error("Impossible de lister les modèles")
        except Exception as e:
            logger.error(f"Erreur: {e}")
    
    def show_disk_usage(self):
        """Affiche l'utilisation disque."""
        print("\n=== Utilisation disque ===\n")
        
        # Dossier Ollama (emplacements courants)
        ollama_paths = [
            Path.home() / ".ollama",  # Linux/Mac
            Path("C:\\Users") / os.getlogin() / "AppData" / "Local" / "Ollama",  # Windows
        ]
        
        total_size = 0
        
        for path in ollama_paths:
            if path.exists():
                size = sum(
                    f.stat().st_size for f in path.rglob('*') if f.is_file()
                )
                size_gb = size / (1024**3)
                print(f"Ollama ({path}): {size_gb:.2f} GB")
                total_size += size
        
        # Data local
        if self.data_dir.exists():
            size = sum(
                f.stat().st_size for f in self.data_dir.rglob('*') if f.is_file()
            )
            size_mb = size / (1024**2)
            print(f"Data projet: {size_mb:.2f} MB")
            total_size += size
        
        total_gb = total_size / (1024**3)
        print(f"\nTotal: {total_gb:.2f} GB")
    
    def clean_temp_files(self):
        """Nettoie les fichiers temporaires."""
        print("\n=== Nettoyage fichiers temporaires ===\n")
        
        patterns = ["*_temp.docx", "*.tmp", "*.temp", "*~"]
        removed_count = 0
        
        for pattern in patterns:
            for file in self.backend_dir.rglob(pattern):
                try:
                    file.unlink()
                    print(f"✓ Supprimé: {file}")
                    removed_count += 1
                except Exception as e:
                    logger.error(f"Impossible de supprimer {file}: {e}")
        
        print(f"\n{removed_count} fichiers supprimés")
    
    def clean_old_results(self, days=30):
        """Nettoie les anciens résultats JSON."""
        print(f"\n=== Nettoyage résultats > {days} jours ===\n")
        
        if not self.output_dir.exists():
            print("Pas de dossier output")
            return
        
        removed_count = 0
        threshold = datetime.now().timestamp() - (days * 24 * 3600)
        
        for json_file in self.output_dir.glob("*.json"):
            if json_file.stat().st_mtime < threshold:
                try:
                    json_file.unlink()
                    print(f"✓ Supprimé: {json_file.name}")
                    removed_count += 1
                except Exception as e:
                    logger.error(f"Impossible de supprimer {json_file}: {e}")
        
        print(f"\n{removed_count} fichiers supprimés")
    
    def check_mistral_health(self):
        """Vérifie la santé de Mistral."""
        print("\n=== Vérification santé Mistral ===\n")
        
        from extractors.mistral_analyzer import verify_mistral_setup
        
        status = verify_mistral_setup()
        
        print(f"Status: {status['status']}")
        print(f"Ollama accessible: {status['ollama_accessible']}")
        print(f"Mistral téléchargé: {status['mistral_downloaded']}")
        
        if status['status'] == 'OK':
            print("\n✓ Mistral est prêt!")
        else:
            print("\n✗ Problèmes détectés:")
            for step in status['next_steps']:
                print(f"  - {step}")
    
    def restart_ollama(self):
        """Redémarre Ollama."""
        print("\n=== Redémarrage Ollama ===\n")
        
        print("Pour redémarrer Ollama:")
        print("1. Fermez tous les terminaux avec 'ollama serve'")
        print("2. Attendez 5 secondes")
        print("3. Exécutez: ollama serve\n")
        
        input("Appuyez sur Entrée une fois Ollama redémarré...")
    
    def pull_mistral_update(self):
        """Télécharge une nouvelle version de Mistral."""
        print("\n=== Mise à jour Mistral ===\n")
        
        print("Téléchargement de la dernière version de Mistral...")
        print("(Cela peut prendre plusieurs minutes)\n")
        
        try:
            subprocess.run(["ollama", "pull", "mistral"])
            print("\n✓ Mise à jour terminée")
        except Exception as e:
            logger.error(f"Erreur: {e}")
    
    def remove_all_models(self):
        """Supprime tous les modèles Ollama."""
        print("\n=== Suppression tous les modèles ===\n")
        print("ATTENTION: Cela supprimera tous les modèles (~5-10 GB)")
        response = input("Êtes-vous sûr? (o/n): ").strip().lower()
        
        if response not in ['o', 'y', 'yes', 'oui']:
            print("Annulé")
            return
        
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                removed = 0
                
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        print(f"Suppression de {model_name}...")
                        subprocess.run(["ollama", "rm", model_name])
                        removed += 1
                
                print(f"\n✓ {removed} modèles supprimés")
        except Exception as e:
            logger.error(f"Erreur: {e}")
    
    def show_recent_logs(self, lines=50):
        """Affiche les logs récents."""
        print(f"\n=== Derniers {lines} logs ===\n")
        
        # Chercher les fichiers de log
        log_files = list(self.backend_dir.glob("*.log"))
        
        if not log_files:
            print("Pas de fichier de log trouvé")
            return
        
        # Afficher le plus récent
        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            for line in all_lines[-lines:]:
                print(line.rstrip())
    
    def export_results(self):
        """Exporte les résultats."""
        print("\n=== Export des résultats ===\n")
        
        if not self.output_dir.exists():
            print("Pas de résultats à exporter")
            return
        
        json_files = list(self.output_dir.glob("*.json"))
        
        print(f"Résultats trouvés: {len(json_files)}")
        
        # Créer un archive
        import shutil
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"cv_results_export_{timestamp}"
        
        try:
            archive_path = shutil.make_archive(
                str(self.backend_dir / archive_name),
                'zip',
                str(self.output_dir)
            )
            print(f"✓ Export créé: {archive_path}")
        except Exception as e:
            logger.error(f"Erreur: {e}")
    
    def run(self):
        """Boucle principale."""
        while True:
            self.print_menu()
            
            choice = input("Entrez votre choix (1-11): ").strip()
            
            try:
                if choice == "1":
                    self.list_ollama_models()
                elif choice == "2":
                    self.show_disk_usage()
                elif choice == "3":
                    self.clean_temp_files()
                elif choice == "4":
                    days = input("Supprimer les résultats > N jours? (30): ").strip()
                    days = int(days) if days else 30
                    self.clean_old_results(days)
                elif choice == "5":
                    self.check_mistral_health()
                elif choice == "6":
                    self.restart_ollama()
                elif choice == "7":
                    self.pull_mistral_update()
                elif choice == "8":
                    self.remove_all_models()
                elif choice == "9":
                    lines = input("Nombre de lignes? (50): ").strip()
                    lines = int(lines) if lines else 50
                    self.show_recent_logs(lines)
                elif choice == "10":
                    self.export_results()
                elif choice == "11":
                    print("\nAu revoir!")
                    break
                else:
                    print("Choix invalide")
                
                input("\nAppuyez sur Entrée pour continuer...")
                
            except ValueError as e:
                logger.error(f"Entrée invalide: {e}")
            except KeyboardInterrupt:
                print("\n\nAnnulé")
                break
            except Exception as e:
                logger.error(f"Erreur: {e}")


def main():
    """Point d'entrée."""
    maintenance = MistralMaintenance()
    
    try:
        maintenance.run()
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
