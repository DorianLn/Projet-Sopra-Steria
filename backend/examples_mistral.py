"""
Exemples d'utilisation du module Mistral pour l'analyse de CV.
"""

import json
from pathlib import Path
from extractors.mistral_analyzer import analyze_cv, verify_mistral_setup, MistralCVAnalyzer


# ============================================================================
# EXEMPLE 1: Utilisation basique avec la fonction wrapper
# ============================================================================

def exemple_simple():
    """Exemple le plus simple."""
    print("=" * 60)
    print("EXEMPLE 1: Utilisation simple")
    print("=" * 60)
    
    cv_text = """
    Jean Dupont
    Email: jean.dupont@example.com
    Téléphone: 06 12 34 56 78
    
    EXPÉRIENCE PROFESSIONNELLE:
    - De 2020 à 2023: Développeur Python Senior chez Acme Corp, Paris
      Développement d'applications web avec Django et FastAPI.
      Gestion d'une équipe de 3 développeurs.
    
    - De 2018 à 2020: Développeur Python Junior chez TechStart, Lyon
      Développement backend. Introduction aux bonnes pratiques.
    
    FORMATION:
    - 2018: Master Informatique, Université Pierre et Marie Curie, Paris
    - 2016: Licence Informatique, Université Pierre et Marie Curie, Paris
    
    COMPÉTENCES:
    - Langages: Python, JavaScript, SQL
    - Frameworks: Django, FastAPI, React
    - Outils: Docker, Kubernetes, Git, PostgreSQL, MongoDB
    
    LANGUES:
    - Français (natif)
    - Anglais (courant)
    - Espagnol (intermédiaire)
    
    CERTIFICATIONS:
    - AWS Solutions Architect Associate (2021)
    """
    
    print("\nAnalyse en cours...\n")
    result = analyze_cv(cv_text)
    
    if result:
        print("✓ Analyse réussie!\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("✗ Erreur lors de l'analyse")
    
    return result


# ============================================================================
# EXEMPLE 2: Utilisation avec la classe directement
# ============================================================================

def exemple_avec_classe():
    """Exemple en utilisant la classe directement."""
    print("\n" + "=" * 60)
    print("EXEMPLE 2: Utilisation avec la classe MistralCVAnalyzer")
    print("=" * 60)
    
    # Créer une instance
    analyzer = MistralCVAnalyzer(ollama_host="http://localhost:11434")
    
    # Vérifier le setup
    print("\nVérification du setup...")
    if not analyzer.is_ollama_running():
        print("✗ Ollama n'est pas accessible")
        return None
    
    if not analyzer.is_mistral_available():
        print("✗ Mistral n'est pas téléchargé")
        return None
    
    print("✓ Setup OK")
    
    # Analyser
    cv_text = """
    Marie Laurent
    Paris, 75001
    Email: marie.laurent@example.com
    Tél: 06 98 76 54 32
    
    EXPÉRIENCE:
    Développeuse Full Stack chez CloudTech (2021-2024)
    - Python, Django, PostgreSQL
    - React, Node.js, Docker
    
    Développeuse Backend chez DataCore (2019-2021)
    - Python, Flask, MongoDB
    
    ÉTUDES:
    Master Informatique - Université de Paris (2019)
    Licence Informatique - Université de Paris (2017)
    
    COMPÉTENCES: Python, JavaScript, SQL, Docker, Git
    LANGUES: Français, Anglais, Allemand
    """
    
    print("\nAnalyse en cours...")
    result = analyzer.analyze_cv(cv_text)
    
    if result:
        print("✓ Analyse réussie!\n")
        return result
    else:
        print("✗ Erreur lors de l'analyse")
        return None


# ============================================================================
# EXEMPLE 3: Traiter un fichier CV
# ============================================================================

def exemple_depuis_fichier(filepath: str):
    """Analyse un CV depuis un fichier texte."""
    print("\n" + "=" * 60)
    print("EXEMPLE 3: Analyse depuis un fichier")
    print("=" * 60)
    
    file_path = Path(filepath)
    
    if not file_path.exists():
        print(f"✗ Fichier non trouvé: {filepath}")
        return None
    
    print(f"\nLecture du fichier: {filepath}")
    with open(file_path, 'r', encoding='utf-8') as f:
        cv_text = f.read()
    
    print(f"Texte lu: {len(cv_text)} caractères")
    print("\nAnalyse en cours...")
    
    result = analyze_cv(cv_text)
    
    if result:
        print("✓ Analyse réussie!\n")
        return result
    else:
        print("✗ Erreur lors de l'analyse")
        return None


# ============================================================================
# EXEMPLE 4: Vérifier le setup Mistral
# ============================================================================

def exemple_verification_setup():
    """Vérifie le setup de Mistral."""
    print("\n" + "=" * 60)
    print("EXEMPLE 4: Vérification du setup")
    print("=" * 60)
    
    status = verify_mistral_setup()
    
    print("\nÉtat du système:")
    for key, value in status.items():
        if key == "next_steps":
            print("\nÉtapes recommandées:")
            for step in value:
                print(f"  - {step}")
        else:
            print(f"  {key}: {value}")
    
    return status


# ============================================================================
# EXEMPLE 5: Traiter plusieurs CVs en batch
# ============================================================================

def exemple_batch_processing(cv_texts: list):
    """Traite plusieurs CVs."""
    print("\n" + "=" * 60)
    print(f"EXEMPLE 5: Traitement batch ({len(cv_texts)} CVs)")
    print("=" * 60)
    
    analyzer = MistralCVAnalyzer()
    results = []
    
    for i, cv_text in enumerate(cv_texts, 1):
        print(f"\nCV {i}/{len(cv_texts)}...")
        result = analyzer.analyze_cv(cv_text)
        
        if result:
            results.append({
                "cv_number": i,
                "status": "success",
                "data": result
            })
            print(f"✓ CV {i} analysé avec succès")
        else:
            results.append({
                "cv_number": i,
                "status": "error",
                "error": "Impossible d'analyser"
            })
            print(f"✗ Erreur pour CV {i}")
    
    print(f"\n✓ Traitement complété: {sum(1 for r in results if r['status'] == 'success')}/{len(cv_texts)} réussis")
    
    return results


# ============================================================================
# EXEMPLE 6: Sauvegarder les résultats
# ============================================================================

def exemple_sauvegarder_resultats(cv_text: str, output_path: str = "cv_result.json"):
    """Analyse un CV et sauvegarde le résultat."""
    print("\n" + "=" * 60)
    print("EXEMPLE 6: Analyse et sauvegarde")
    print("=" * 60)
    
    print("\nAnalyse en cours...")
    result = analyze_cv(cv_text)
    
    if result:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Résultat sauvegardé: {output_path}")
        return result
    else:
        print("✗ Erreur lors de l'analyse")
        return None


# ============================================================================
# EXEMPLE 7: Gestion d'erreurs et retry
# ============================================================================

def exemple_avec_gestion_erreurs():
    """Montre comment gérer les erreurs."""
    print("\n" + "=" * 60)
    print("EXEMPLE 7: Gestion d'erreurs")
    print("=" * 60)
    
    analyzer = MistralCVAnalyzer()
    
    # Test 1: CV vide
    print("\nTest 1: CV vide")
    result = analyzer.analyze_cv("")
    if result:
        print("  ✓ Analysé")
    else:
        print("  ✗ Erreur (attendu)")
    
    # Test 2: Vérifier Ollama
    print("\nTest 2: Vérification Ollama")
    if analyzer.is_ollama_running():
        print("  ✓ Ollama accessible")
    else:
        print("  ✗ Ollama non accessible")
        print("    Solution: Lancez 'ollama serve' dans un autre terminal")
    
    # Test 3: Vérifier Mistral
    print("\nTest 3: Vérification Mistral")
    if analyzer.is_mistral_available():
        print("  ✓ Mistral téléchargé")
    else:
        print("  ✗ Mistral non téléchargé")
        print("    Solution: Lancez 'ollama pull mistral'")


# ============================================================================
# Main: Exécuter les exemples
# ============================================================================

def main():
    """Exécute tous les exemples."""
    
    print("\n" + "=" * 60)
    print("EXEMPLES D'UTILISATION - MISTRAL CV ANALYZER")
    print("=" * 60)
    
    # Exemple 1: Utilisation simple
    try:
        result1 = exemple_simple()
    except Exception as e:
        print(f"\n✗ Erreur exemple 1: {e}")
    
    # Exemple 2: Avec la classe
    try:
        result2 = exemple_avec_classe()
    except Exception as e:
        print(f"\n✗ Erreur exemple 2: {e}")
    
    # Exemple 4: Vérification setup
    try:
        status = exemple_verification_setup()
    except Exception as e:
        print(f"\n✗ Erreur exemple 4: {e}")
    
    # Exemple 7: Gestion d'erreurs
    try:
        exemple_avec_gestion_erreurs()
    except Exception as e:
        print(f"\n✗ Erreur exemple 7: {e}")
    
    # Exemple 6: Sauvegarde
    cv_sample = """
    Pierre Martin
    Email: pierre.martin@example.com
    
    Ingénieur Logiciel - TechCorp (2021-2024)
    - Python, Django, PostgreSQL
    
    Master Informatique - Université Paris-Saclay (2021)
    """
    
    try:
        exemple_sauvegarder_resultats(
            cv_sample,
            "backend/data/output/exemple_result.json"
        )
    except Exception as e:
        print(f"\n✗ Erreur exemple 6: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Exemples terminés")
    print("=" * 60)


if __name__ == "__main__":
    main()
