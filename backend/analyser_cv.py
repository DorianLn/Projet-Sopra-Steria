import os
import re
import json
from docx import Document

from extractors.extracteur import extraire_dates, extraire_email, extraire_telephone, extraire_adresse
from extractors.section_classifier import extraire_par_sections
from extractors.enhanced_extractor import completer_donnees_manquantes
from extractors.heuristic_rules import extract_job_title_heuristic, extract_diploma_heuristic
from extractors.spacy_extractor import separer_competences
from extractors.heuristic_rules import extract_structured_cv_data
from extractors.extracteur import extraire_nom_prenom
from extractors.extracteur import extraire_experiences, extraire_formations
from normalizers.skill_cleaner import nettoyer_competences_json





def lire_cv_docx(chemin_fichier):
    doc = Document(chemin_fichier)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def extraire_infos_cv(texte_cv):
    return {
        "dates": extraire_dates(texte_cv),
        "emails": extraire_email(texte_cv),
        "telephones": extraire_telephone(texte_cv),
        "adresses": extraire_adresse(texte_cv)
    }
    

def extraire_cv_pipeline(texte_cv):

    # Extraction brute initiale
    infos = extraire_infos_cv(texte_cv)

    # 1. Découpage par sections
    sections = extraire_par_sections(texte_cv)

    # Ajout extraction structurée heuristique
    heuristic_global = extract_structured_cv_data(texte_cv)

    # 2. Extraction contact CORRIGÉE
    contact = {
        "email": infos["emails"][0] if infos["emails"] else None,
        "telephone": infos["telephones"][0] if infos["telephones"] else None,
        "adresse": infos["adresses"][0] if infos["adresses"] else None,
        "nom": extraire_nom_prenom(texte_cv)   
    }

    # 3. Expériences via  extracteur existant + heuristique
    exp_regex = extraire_experiences(sections["experiences_text"])

    exp_heuristic = extract_job_title_heuristic(sections["experiences_text"])

    # Fusion des deux sources
    experiences_struct = []

    # D'abord celles issues de regex
    for exp in exp_regex:
        if " - " in exp:
            poste, entreprise = exp.split(" - ", 1)
        else:
            poste = exp
            entreprise = None

        experiences_struct.append({
            "poste": poste,
            "entreprise": entreprise,
            "source": "regex"
        })

    # Puis celles issues des heuristiques
    for h in exp_heuristic:
        experiences_struct.append({
            "poste": h["title"],
            "entreprise": None,
            "source": "heuristique"
        })

    # 4. Formations via  extracteur existant + heuristique
    form_regex = extraire_formations(sections["formations_text"])
    form_heuristic = extract_diploma_heuristic(sections["formations_text"])

    # Fusion des deux sources
    formations_struct = []
    
    for f in form_regex:
        formations_struct.append({
            "diplome": f,
            "source": "regex"
        })

    for h in form_heuristic:
        formations_struct.append({
            "diplome": h["diploma"],
            "source": "heuristique"
        })

    # Filtrage des entrées non pertinentes
    formations_struct = [
    f for f in formations_struct
    if not re.search(r"\b(M|chez|juillet|janvier|mars|avril)\b", f["diplome"], re.IGNORECASE)
    ]

    # 5. Compétences – vraie extraction
    competences_brutes = sections["competences_text"]

    # On sépare par virgules + lignes
    competences_list = re.split(r"[,\n•\-]", competences_brutes)

    competences_list = [
        c.strip()
        for c in competences_list
        if len(c.strip()) > 2
    ]

    # Étape 1 : séparation techniques / fonctionnelles
    competences_separees = separer_competences(competences_list)

    # Étape 2 : nettoyage final des compétences
    competences = nettoyer_competences_json(competences_separees)

    # 6. Langues – ok
    langues = [
        l.strip()
        for l in sections["langues_text"].split("\n")
        if l.strip()
    ]

    structure = {
        "contact": contact,
        "formations": formations_struct,
        "experiences": experiences_struct,
        "competences": competences,
        "langues": langues
    }

    # 7. Complétion par NER si besoin
    structure = completer_donnees_manquantes(structure, texte_cv)

    return structure


def analyser_cv():
    dossier_input = "data/input"
    dossier_output = "data/output"

    os.makedirs(dossier_output, exist_ok=True)

    fichiers_cv = [f for f in os.listdir(dossier_input) if f.endswith('.docx')]
    if not fichiers_cv:
        print("Aucun CV (.docx) trouvé dans data/input")
        return

    for fichier in fichiers_cv:
        chemin_cv = os.path.join(dossier_input, fichier)
        texte_cv = lire_cv_docx(chemin_cv)

        resultats = extraire_cv_pipeline(texte_cv)

        nom_json = os.path.splitext(fichier)[0] + "_resultats.json"
        chemin_sortie = os.path.join(dossier_output, nom_json)

        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)

        print("Analyse OK →", chemin_sortie)


if __name__ == "__main__":
    analyser_cv()
