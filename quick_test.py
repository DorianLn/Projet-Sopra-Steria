#!/usr/bin/env python3
"""
Test de vérification rapide - Mistral 7B
Lance quelques vérifications basiques et simples pour s'assurer que tout fonctionne.
"""

import sys
from pathlib import Path

# Ajouter le backend au path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_1_imports():
    """Test 1: Vérifier que les modules peuvent être importés."""
    print("\n" + "=" * 60)
    print("TEST 1: IMPORTS")
    print("=" * 60)
    
    try:
        from extractors.mistral_analyzer import (
            MistralCVAnalyzer,
            analyze_cv,
            verify_mistral_setup
        )
        print("✓ Tous les imports réussis")
        return True
    except ImportError as e:
        print(f"✗ Erreur d'import: {e}")
        return False


def test_2_verify_setup():
    """Test 2: Vérifier le setup de Mistral."""
    print("\n" + "=" * 60)
    print("TEST 2: VÉRIFICATION DU SETUP")
    print("=" * 60)
    
    try:
        from extractors.mistral_analyzer import verify_mistral_setup
        
        status = verify_mistral_setup()
        
        print(f"Status: {status['status']}")
        print(f"Ollama accessible: {status['ollama_accessible']}")
        print(f"Mistral disponible: {status['mistral_downloaded']}")
        
        if status['status'] == 'OK':
            print("✓ Setup OK - Mistral est prêt!")
            return True
        else:
            print("⚠ Setup incomplet:")
            for step in status['next_steps']:
                print(f"  - {step}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_3_analyzer_init():
    """Test 3: Initialiser l'analyseur."""
    print("\n" + "=" * 60)
    print("TEST 3: INITIALISATION DE L'ANALYSEUR")
    print("=" * 60)
    
    try:
        from extractors.mistral_analyzer import MistralCVAnalyzer
        
        analyzer = MistralCVAnalyzer()
        
        print(f"✓ MistralCVAnalyzer créé")
        print(f"  Host: {analyzer.ollama_host}")
        print(f"  Model: {analyzer.model_name}")
        print(f"  Max retries: {analyzer.max_retries}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_4_json_parsing():
    """Test 4: Tester le parsing JSON."""
    print("\n" + "=" * 60)
    print("TEST 4: PARSING JSON")
    print("=" * 60)
    
    try:
        from extractors.mistral_analyzer import MistralCVAnalyzer
        
        analyzer = MistralCVAnalyzer()
        
        # Test JSON valide
        test_json = '{"nom": "Dupont", "prenom": "Jean"}'
        result = analyzer._parse_json_response(test_json)
        
        if result and result.get("nom") == "Dupont":
            print("✓ Parsing JSON valide")
        else:
            print("✗ Parsing JSON échoué")
            return False
        
        # Test JSON invalide
        test_invalid = '{"nom": invalid}'
        result = analyzer._parse_json_response(test_invalid)
        
        if result is None:
            print("✓ Rejet JSON invalide")
        else:
            print("✗ JSON invalide accepté")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_5_prompt_building():
    """Test 5: Construire un prompt."""
    print("\n" + "=" * 60)
    print("TEST 5: CONSTRUCTION DU PROMPT")
    print("=" * 60)
    
    try:
        from extractors.mistral_analyzer import MistralCVAnalyzer
        
        analyzer = MistralCVAnalyzer()
        
        cv_text = "Jean Dupont\nDéveloppeur Python"
        prompt = analyzer._build_prompt(cv_text)
        
        # Vérifier que le prompt contient les éléments clés
        checks = [
            ("Analyse ce CV" in prompt, "Contient instruction"),
            ("JSON structuré" in prompt, "Demande JSON"),
            ("identite" in prompt, "Contient champ identite"),
            (cv_text in prompt, "Contient le CV")
        ]
        
        all_ok = True
        for check, desc in checks:
            if check:
                print(f"  ✓ {desc}")
            else:
                print(f"  ✗ {desc}")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_6_function_wrapper():
    """Test 6: Tester la fonction wrapper."""
    print("\n" + "=" * 60)
    print("TEST 6: FONCTION WRAPPER")
    print("=" * 60)
    
    try:
        from extractors.mistral_analyzer import analyze_cv
        
        # Tester que la fonction existe
        print(f"✓ Fonction analyze_cv() importée")
        print(f"  Type: {type(analyze_cv)}")
        print(f"  Callable: {callable(analyze_cv)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def main():
    """Lancer tous les tests."""
    print("\n" + "🧪 TESTS RAPIDES - MISTRAL 7B".center(60))
    print("=" * 60)
    
    results = {
        "Imports": test_1_imports(),
        "Setup Mistral": test_2_verify_setup(),
        "Analyseur": test_3_analyzer_init(),
        "JSON Parsing": test_4_json_parsing(),
        "Prompt Building": test_5_prompt_building(),
        "Function Wrapper": test_6_function_wrapper(),
    }
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}")
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS PASSENT!")
        print("\nVous pouvez maintenant:")
        print("1. Installer Ollama si pas déjà fait")
        print("2. Lancer 'ollama serve' dans un terminal")
        print("3. Télécharger Mistral: 'ollama pull mistral'")
        print("4. Utiliser le code Python!")
        return 0
    elif passed >= total - 1:
        print("\n⚠️  Certains tests ont échoué")
        print("\nVérifiez:")
        print("1. Ollama est installé et lancé")
        print("2. Mistral est téléchargé")
        print("3. Le chemin Python est correct")
        return 1
    else:
        print("\n❌ PLUSIEURS TESTS ONT ÉCHOUÉ")
        print("\nVérifiez:")
        print("1. Les imports: 'python -c \"from extractors.mistral_analyzer import analyze_cv\"'")
        print("2. Le setup: 'python backend/startup.py'")
        print("3. Les logs pour plus de détails")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
