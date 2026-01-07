"""
Script de test pour vérifier l'intégration du modèle entraîné
"""
from extractors.pdf_to_docx import convert_pdf_to_docx
from analyser_cv import lire_cv_docx, extraire_infos_cv
from extractors.section_classifier import build_structured_json
from pathlib import Path
import json
import sys

def test_extraction(cv_name="CV_LEO_WEBER_1"):
    # Test avec un CV
    pdf_path = Path(f'data/input/{cv_name}.pdf')
    docx_path = Path(f'data/input/{cv_name}_test.docx')
    
    if pdf_path.exists():
        convert_pdf_to_docx(str(pdf_path), str(docx_path))
    
    if not docx_path.exists():
        print(f"Fichier non trouvé: {docx_path}")
        return
    
    # Lecture
    texte_cv = lire_cv_docx(str(docx_path))
    
    # Extraction brute
    infos = extraire_infos_cv(texte_cv)
    
    # Build complet
    result = build_structured_json(
        emails=infos['emails'],
        telephones=infos['telephones'],
        adresses=infos['adresses'],
        dates=infos['dates'],
        texte_cv=texte_cv
    )
    
    print(f'\n=== RESULTAT pour {cv_name} ===')
    print(f"Nom: {result['contact']['nom']}")
    print(f"Email: {result['contact']['email']}")
    print(f"Langues: {result['langues']}")
    print(f"\nFormations ({len(result['formations'])}):")
    for f in result['formations'][:3]:
        print(f'  - {f}')
    print(f"\nExpériences ({len(result['experiences'])}):")
    for e in result['experiences'][:5]:
        print(f'  - {e}')
    print(f"\nCompétences: {result['competences'][:10]}")

if __name__ == "__main__":
    cv_name = sys.argv[1] if len(sys.argv) > 1 else "CV_LEO_WEBER_1"
    test_extraction(cv_name)
