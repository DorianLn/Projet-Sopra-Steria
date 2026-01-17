"""
Script de test pour vérifier l'intégration complète du pipeline actuel
"""
from extractors.pdf_to_docx import convert_pdf_to_docx
from analyser_cv import lire_cv_docx, extraire_cv_pipeline
from pathlib import Path
import json
import sys


def test_extraction(cv_name="CV_LEO_WEBER_1"):
    # Test avec un CV
    pdf_path = Path(f'data/input/{cv_name}.pdf')
    docx_path = Path(f'data/input/{cv_name}_test.docx')

    # Conversion si besoin
    if pdf_path.exists():
        print(f"Conversion PDF → DOCX : {pdf_path}")
        convert_pdf_to_docx(str(pdf_path), str(docx_path))

    if not docx_path.exists():
        print(f"Fichier non trouvé: {docx_path}")
        return

    # Lecture
    texte_cv = lire_cv_docx(str(docx_path))

    # 🔥 ICI : on utilise TON pipeline complet actuel
    result = extraire_cv_pipeline(texte_cv)

    print(f'\n=== RESULTAT pour {cv_name} ===')

    print("\n--- CONTACT ---")
    print(f"Nom: {result['contact'].get('nom')}")
    print(f"Email: {result['contact'].get('email')}")
    print(f"Téléphone: {result['contact'].get('telephone')}")

    print("\n--- LANGUES ---")
    print(result.get("langues", []))

    print(f"\n--- FORMATIONS ({len(result.get('formations', []))}) ---")
    for f in result.get("formations", [])[:3]:
        print(f'  - {f}')

    print(f"\n--- EXPÉRIENCES ({len(result.get('experiences', []))}) ---")
    for e in result.get("experiences", [])[:5]:
        print(f'  - {e}')

    print("\n--- COMPÉTENCES ---")
    print(json.dumps(result.get("competences", {}), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    cv_name = sys.argv[1] if len(sys.argv) > 1 else "CV_LEO_WEBER_1"
    test_extraction(cv_name)
