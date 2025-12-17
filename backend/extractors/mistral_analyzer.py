"""
Module d'analyse de CV utilisant Mistral 7B via Ollama en local.
Nécessite Ollama installé et le modèle Mistral lancé.
"""

import json
import logging
import time
from typing import Dict, Optional, Any
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class MistralCVAnalyzer:
    """Analyseur de CV utilisant Mistral local via Ollama."""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """
        Initialise l'analyseur Mistral.
        
        Args:
            ollama_host: URL du serveur Ollama (par défaut localhost:11434)
        """
        self.ollama_host = ollama_host
        self.model_name = "mistral"
        self.api_endpoint = f"{ollama_host}/api/generate"
        self.max_retries = 3
        self.retry_delay = 2  # secondes
        
    def is_ollama_running(self) -> bool:
        """Vérifie si Ollama est accessible."""
        try:
            req = urllib.request.Request(
                f"{self.ollama_host}/api/tags",
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except (urllib.error.URLError, Exception):
            return False
    
    def is_mistral_available(self) -> bool:
        """Vérifie si le modèle Mistral est téléchargé."""
        try:
            req = urllib.request.Request(
                f"{self.ollama_host}/api/tags",
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                models = data.get("models", [])
                return any(
                    model.get("name", "").startswith("mistral")
                    for model in models
                )
        except (urllib.error.URLError, Exception):
            return False
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extrait le JSON valide d'une réponse Mistral.
        
        Args:
            text: Texte complet de la réponse
            
        Returns:
            Dict contenant le JSON parsé, ou None
        """
        # Essaie de trouver les limites du JSON
        start_idx = text.find('{')
        if start_idx == -1:
            return None
        
        # Compte les accolades pour trouver la fin du JSON
        brace_count = 0
        end_idx = start_idx
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx == start_idx:
            return None
        
        try:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error(f"Erreur parsing JSON: {json_str[:100]}")
            return None
    
    def analyze_cv(self, cv_text: str) -> Optional[Dict[str, Any]]:
        """
        Analyse un CV avec Mistral et retourne du JSON structuré.
        
        Args:
            cv_text: Texte du CV à analyser
            
        Returns:
            Dict contenant les informations structurées du CV, ou None en cas d'erreur
        """
        # Validation préalable
        if not cv_text or not cv_text.strip():
            logger.error("Le texte du CV ne peut pas être vide")
            return None
        
        # Vérifications
        if not self.is_ollama_running():
            logger.error(
                f"Ollama n'est pas accessible à {self.ollama_host}. "
                "Assurez-vous qu'Ollama est lancé (ollama serve)"
            )
            return None
        
        if not self.is_mistral_available():
            logger.error(
                "Le modèle Mistral n'est pas téléchargé. "
                "Lancez: ollama pull mistral"
            )
            return None
        
        # Construction du prompt
        prompt = self._build_prompt(cv_text)
        
        # Appel à Ollama
        for attempt in range(self.max_retries):
            try:
                response_text = self._call_ollama(prompt)
                
                if response_text:
                    # Parse la réponse JSON
                    parsed_json = self._parse_json_response(response_text)
                    
                    if parsed_json:
                        logger.info("Analyse Mistral réussie")
                        return parsed_json
                    else:
                        logger.warning(
                            f"Tentative {attempt + 1}: "
                            "Impossible de parser le JSON de la réponse"
                        )
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay)
                            continue
                        else:
                            return None
            except Exception as e:
                logger.error(f"Tentative {attempt + 1} échouée: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return None
        
        return None
    
    def _build_prompt(self, cv_text: str) -> str:
        """
        Construit le prompt pour Mistral.
        
        Args:
            cv_text: Texte du CV
            
        Returns:
            Prompt formaté
        """
        prompt = f"""Analyse ce CV et retourne strictement un JSON structuré avec les champs suivants :
- identite (nom, prenom)
- contact (adresse, ville, code_postal, email, telephone)
- experience (poste, entreprise, ville, date_debut, date_fin, description)
- formation (diplome, ecole, date_debut, date_fin)
- certifications
- langues
- competences
- resume

N'invente rien. Retourne uniquement du JSON valide.

CV :
{cv_text}

JSON:"""
        return prompt
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        Appelle l'API Ollama avec le prompt.
        
        Args:
            prompt: Prompt à envoyer
            
        Returns:
            Texte de la réponse complète
        """
        try:
            request_data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,  # Température basse pour plus de déterminisme
            }
            
            json_data = json.dumps(request_data).encode('utf-8')
            
            req = urllib.request.Request(
                self.api_endpoint,
                data=json_data,
                headers={'Content-Type': 'application/json'},
                method="POST"
            )
            
            logger.info("Appel Ollama en cours...")
            with urllib.request.urlopen(req, timeout=300) as response:
                response_data = json.loads(response.read().decode())
                response_text = response_data.get("response", "")
                logger.debug(f"Réponse Ollama: {response_text[:200]}")
                return response_text
                
        except urllib.error.HTTPError as e:
            logger.error(f"Erreur HTTP Ollama: {e.code} - {e.reason}")
            return None
        except urllib.error.URLError as e:
            logger.error(f"Erreur connexion Ollama: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing réponse JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel Ollama: {str(e)}")
            return None


# Fonction wrapper pour compatibilité avec le reste du projet
def analyze_cv(text: str) -> Optional[Dict[str, Any]]:
    """
    Fonction principale d'analyse de CV avec Mistral.
    
    Args:
        text: Texte du CV à analyser
        
    Returns:
        Dict contenant les informations structurées du CV
    """
    analyzer = MistralCVAnalyzer()
    return analyzer.analyze_cv(text)


# Fonction de setup/vérification
def verify_mistral_setup() -> Dict[str, Any]:
    """
    Vérifie l'état du setup Mistral/Ollama.
    
    Returns:
        Dict avec l'état de chaque composant
    """
    analyzer = MistralCVAnalyzer()
    
    return {
        "ollama_accessible": analyzer.is_ollama_running(),
        "mistral_downloaded": analyzer.is_mistral_available(),
        "ollama_host": analyzer.ollama_host,
        "model_name": analyzer.model_name,
        "status": "OK" if (analyzer.is_ollama_running() and 
                           analyzer.is_mistral_available()) else "ERROR",
        "next_steps": _get_next_steps(
            analyzer.is_ollama_running(),
            analyzer.is_mistral_available()
        )
    }


def _get_next_steps(ollama_running: bool, mistral_available: bool) -> list:
    """Retourne les étapes suivantes en fonction du setup."""
    steps = []
    
    if not ollama_running:
        steps.append("1. Installez Ollama: https://ollama.ai/download")
        steps.append("2. Lancez Ollama: ollama serve")
    
    if ollama_running and not mistral_available:
        steps.append("3. Téléchargez Mistral: ollama pull mistral")
    
    if ollama_running and mistral_available:
        steps.append("✓ Mistral est prêt à l'emploi!")
    
    return steps


if __name__ == "__main__":
    # Test du setup
    print("=== Vérification du setup Mistral ===\n")
    status = verify_mistral_setup()
    
    for key, value in status.items():
        if key != "next_steps":
            print(f"{key}: {value}")
    
    print("\nÉtapes suivantes:")
    for step in status["next_steps"]:
        print(f"  {step}")
    
    # Test avec un CV exemple si tout est OK
    if status["status"] == "OK":
        print("\n=== Test avec un CV exemple ===\n")
        sample_cv = """
        Jean Dupont
        Email: jean.dupont@example.com
        Téléphone: 06 12 34 56 78
        
        EXPÉRIENCE:
        - 2020-2023: Développeur Python, Acme Corp, Paris
        - 2018-2020: Stage Développeur, TechStart, Lyon
        
        FORMATION:
        - 2018: Master Informatique, Université X
        - 2016: Licence Informatique, Université X
        
        COMPÉTENCES:
        - Python, Django, FastAPI
        - PostgreSQL, MongoDB
        - Docker, Kubernetes
        """
        
        result = analyze_cv(sample_cv)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Erreur lors de l'analyse du CV")
