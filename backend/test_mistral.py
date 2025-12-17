"""
Tests unitaires pour le module Mistral.
Lancez avec: python -m pytest test_mistral.py
"""

import pytest
import json
from pathlib import Path
from extractors.mistral_analyzer import (
    MistralCVAnalyzer,
    analyze_cv,
    verify_mistral_setup,
    _parse_json_response,
)


class TestMistralCVAnalyzer:
    """Tests de la classe MistralCVAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Crée une instance d'analyseur."""
        return MistralCVAnalyzer()
    
    def test_initialization(self, analyzer):
        """Teste l'initialisation."""
        assert analyzer.ollama_host == "http://localhost:11434"
        assert analyzer.model_name == "mistral"
        assert analyzer.max_retries == 3
    
    def test_custom_host(self):
        """Teste la personnalisation de l'hôte."""
        custom_host = "http://192.168.1.1:11434"
        analyzer = MistralCVAnalyzer(ollama_host=custom_host)
        assert analyzer.ollama_host == custom_host
    
    def test_parse_json_response_valid(self, analyzer):
        """Teste le parsing d'une réponse JSON valide."""
        response = '{"nom": "Dupont", "prenom": "Jean"}'
        result = analyzer._parse_json_response(response)
        
        assert result is not None
        assert result["nom"] == "Dupont"
        assert result["prenom"] == "Jean"
    
    def test_parse_json_response_with_text(self, analyzer):
        """Teste le parsing avec du texte avant et après le JSON."""
        response = 'Voici le résultat: {"nom": "Dupont"} Fin du texte'
        result = analyzer._parse_json_response(response)
        
        assert result is not None
        assert result["nom"] == "Dupont"
    
    def test_parse_json_response_invalid(self, analyzer):
        """Teste avec un JSON invalide."""
        response = '{"nom": invalid}'
        result = analyzer._parse_json_response(response)
        
        assert result is None
    
    def test_parse_json_response_no_json(self, analyzer):
        """Teste avec une réponse sans JSON."""
        response = 'Pas de JSON ici'
        result = analyzer._parse_json_response(response)
        
        assert result is None
    
    def test_build_prompt(self, analyzer):
        """Teste la construction du prompt."""
        cv_text = "Jean Dupont\nDéveloppeur"
        prompt = analyzer._build_prompt(cv_text)
        
        assert "Analyse ce CV" in prompt
        assert "JSON structuré" in prompt
        assert "identite" in prompt
        assert cv_text in prompt
    
    def test_analyze_cv_empty_text(self, analyzer):
        """Teste l'analyse avec un texte vide."""
        result = analyzer.analyze_cv("")
        assert result is None
    
    def test_analyze_cv_none_text(self, analyzer):
        """Teste l'analyse avec None."""
        result = analyzer.analyze_cv(None)
        assert result is None


class TestMistralFunctions:
    """Tests des fonctions utilitaires."""
    
    def test_verify_mistral_setup_returns_dict(self):
        """Teste que verify_mistral_setup retourne un dictionnaire."""
        result = verify_mistral_setup()
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "ollama_accessible" in result
        assert "mistral_downloaded" in result
        assert "next_steps" in result
    
    def test_verify_mistral_setup_next_steps(self):
        """Teste les étapes recommandées."""
        result = verify_mistral_setup()
        
        assert isinstance(result["next_steps"], list)
        assert len(result["next_steps"]) > 0


class TestJSONStructure:
    """Tests de la structure JSON attendue."""
    
    def test_required_json_fields(self):
        """Teste que les champs requis sont documentés."""
        required_fields = [
            "identite",
            "contact",
            "experience",
            "formation",
            "certifications",
            "langues",
            "competences",
            "resume",
        ]
        
        # Vérifier que tous les champs sont mentionnés dans le prompt
        analyzer = MistralCVAnalyzer()
        prompt = analyzer._build_prompt("test")
        
        for field in required_fields:
            assert field in prompt


class TestMistralPrompt:
    """Tests du prompt Mistral."""
    
    def test_prompt_has_json_requirement(self):
        """Teste que le prompt demande du JSON."""
        analyzer = MistralCVAnalyzer()
        prompt = analyzer._build_prompt("test")
        
        assert "JSON" in prompt
        assert "valide" in prompt.lower()
    
    def test_prompt_has_no_invention_warning(self):
        """Teste que le prompt avertit contre l'invention."""
        analyzer = MistralCVAnalyzer()
        prompt = analyzer._build_prompt("test")
        
        assert "invente" in prompt.lower() or "n'invente" in prompt.lower()
    
    def test_prompt_includes_cv_text(self):
        """Teste que le prompt inclut le CV."""
        analyzer = MistralCVAnalyzer()
        cv_text = "TEXTE UNIQUE 12345"
        prompt = analyzer._build_prompt(cv_text)
        
        assert "TEXTE UNIQUE 12345" in prompt


class TestErrorHandling:
    """Tests de la gestion d'erreurs."""
    
    def test_analyzer_handles_invalid_url(self):
        """Teste la gestion d'une URL invalide."""
        analyzer = MistralCVAnalyzer(ollama_host="http://invalid-url:99999")
        
        # Devrait retourner False sans erreur
        assert analyzer.is_ollama_running() == False
    
    def test_analyze_cv_graceful_failure(self):
        """Teste que l'analyse échoue gracieusement."""
        analyzer = MistralCVAnalyzer(ollama_host="http://localhost:99999")
        
        result = analyzer.analyze_cv("texte CV")
        # Devrait retourner None, pas lever d'exception
        assert result is None


class TestIntegration:
    """Tests d'intégration."""
    
    @pytest.mark.skipif(
        not MistralCVAnalyzer().is_ollama_running(),
        reason="Ollama n'est pas accessible"
    )
    def test_mistral_online_check(self):
        """Teste la connexion à Ollama (skip si offline)."""
        analyzer = MistralCVAnalyzer()
        
        assert analyzer.is_ollama_running() == True
    
    @pytest.mark.skipif(
        not MistralCVAnalyzer().is_mistral_available(),
        reason="Mistral n'est pas téléchargé"
    )
    def test_mistral_model_available(self):
        """Teste que Mistral est téléchargé (skip si offline)."""
        analyzer = MistralCVAnalyzer()
        
        assert analyzer.is_mistral_available() == True


# ============================================================================
# Tests manuels
# ============================================================================

def manual_test_full_analysis():
    """Test manuel complet d'analyse."""
    print("\n=== Test complet d'analyse ===\n")
    
    cv_text = """
    Pierre Martin
    Email: pierre.martin@example.com
    Téléphone: +33 6 12 34 56 78
    
    EXPÉRIENCE:
    - 2021-2024: Senior Developer, TechCorp, Paris
      Développement en Python, Django, PostgreSQL
    
    - 2019-2021: Developer, StartupXYZ, Lyon
      Full stack JavaScript
    
    FORMATION:
    - 2019: Master Informatique, Université de Lyon
    - 2017: Licence Informatique, Université de Lyon
    
    COMPÉTENCES: Python, JavaScript, Docker, PostgreSQL, Redis
    
    LANGUES: Français, Anglais, Allemand
    """
    
    print("Texte CV:", cv_text[:100], "...\n")
    
    # Vérifier le setup
    print("1. Vérification du setup...")
    status = verify_mistral_setup()
    print(f"   Status: {status['status']}")
    print(f"   Ollama: {status['ollama_accessible']}")
    print(f"   Mistral: {status['mistral_downloaded']}")
    
    if status['status'] != 'OK':
        print("\n⚠️  Mistral n'est pas complètement configuré")
        print("Étapes à suivre:")
        for step in status['next_steps']:
            print(f"  - {step}")
        return
    
    # Analyser
    print("\n2. Analyse du CV...")
    result = analyze_cv(cv_text)
    
    if result:
        print("✓ Analyse réussie!")
        print("\nRésultat JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("✗ Erreur lors de l'analyse")


if __name__ == "__main__":
    # Exécuter le test manuel si pytest n'est pas disponible
    try:
        import sys
        if "--manual" in sys.argv:
            manual_test_full_analysis()
        else:
            print("Lancez avec pytest: python -m pytest test_mistral.py")
            print("Ou avec --manual: python test_mistral.py --manual")
    except Exception as e:
        print(f"Erreur: {e}")
