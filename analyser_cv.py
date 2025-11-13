"""
Script pour extraire les informations d'un CV
"""
import os
import json
from docx import Document
from backend.extractors.extracteur import extraire_dates, extraire_email, extraire_telephone, extraire_adresse

def lire_cv_docx(chemin_fichier):
    """Lit le contenu d'un fichier .docx"""
    doc = Document(chemin_fichier)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def extraire_infos_cv(texte_cv):
    """Retourne les données brutes extraites d'un texte de CV."""
    return {
        "dates": extraire_dates(texte_cv),
        "emails": extraire_email(texte_cv),
        "telephones": extraire_telephone(texte_cv),
        "adresses": extraire_adresse(texte_cv)
    }


def analyser_cv():
    dossier_input = "backend/data/input"
    dossier_output = "backend/data/output"

    os.makedirs(dossier_output, exist_ok=True)

    fichiers_cv = [f for f in os.listdir(dossier_input) if f.endswith('.docx')]
    if not fichiers_cv:
        print("Aucun CV (.docx) trouvé dans backend/data/input")
        return

    for fichier in fichiers_cv:
        chemin_cv = os.path.join(dossier_input, fichier)
        texte_cv = lire_cv_docx(chemin_cv)

        # ➜ On utilise la fonction unique
        resultats = extraire_infos_cv(texte_cv)

        nom_json = os.path.splitext(fichier)[0] + "_resultats.json"
        chemin_sortie = os.path.join(dossier_output, nom_json)

        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)

        print("Analyse OK →", chemin_sortie)


if __name__ == "__main__":
    analyser_cv()