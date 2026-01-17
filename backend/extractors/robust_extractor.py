"""
Extracteur robuste - optimisé pour multiples formats de CV
Basé sur cas réels : Sopra, étudiants, CV seniors
"""

import re
from pathlib import Path
from typing import Dict, List, Any
from docx import Document
import pdfplumber
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==========================================================
# EXTRACTION TEXTE BRUT
# ==========================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=2
                )
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Erreur PDF: {e}")
        raise


def extract_text_from_docx(docx_path: str) -> str:
    try:
        doc = Document(docx_path)
        text = ""

        for p in doc.paragraphs:
            if p.text.strip():
                text += p.text + "\n"

        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text += " | ".join(row_text) + "\n"

        return text

    except Exception as e:
        logger.error(f"Erreur DOCX: {e}")
        raise


def extract_text(file_path: str) -> str:
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(file_path)

    if path.suffix.lower() == ".docx":
        return extract_text_from_docx(file_path)

    raise ValueError("Format non supporté")


# ==========================================================
# NETTOYAGE AVANCÉ
# ==========================================================

def clean_text(text: str) -> str:

    patterns = [
        r"C2\s*–\s*Usage restreint",
        r"C3\s*–\s*Confidentiel",
        r"<\?xml.*?\?>",
        r"<.*?>",
        r"©.*Sopra.*",
        r"\d+/\d+\s*–",
        r"DocumentFile.*",
        r"Page\s*\d+",
    ]

    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)

    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\n\s*\n", "\n", text)

    return text.strip()


# ==========================================================
# DÉTECTION FLEXIBLE DES SECTIONS
# ==========================================================

SECTION_ALIASES = {
    "competences": [
        "COMPETENCES",
        "COMPÉTENCES",
        "COMPETENCES TECHNIQUES",
        "COMPETENCES FONCTIONNELLES",
        "SKILLS",
        "OUTILS"
    ],
    "formations": [
        "FORMATION",
        "FORMATIONS",
        "FORMATION - CERTIFICATION",
        "FORMATIONS ET LANGUES",
        "ETUDES",
        "EDUCATION"
    ],
    "experiences": [
        "EXPERIENCES",
        "EXPÉRIENCES",
        "EXPERIENCES PROFESSIONNELLES",
        "PARCOURS"
    ],
    "langues": [
        "LANGUES",
        "LANGUE(S)",
        "LANGUAGES"
    ],
    "loisirs": [
        "LOISIRS",
        "CENTRES D’INTÉRÊTS",
        "ACTIVITES EXTRA",
        "HOBBIES"
    ]
}


def normalize_title(title: str) -> str:
    title = title.upper().strip()

    for key, aliases in SECTION_ALIASES.items():
        for a in aliases:
            if a in title:
                return key
    return "contact"


def find_sections(text: str) -> Dict[str, str]:

    sections = {
        "contact": "",
        "competences": "",
        "experiences": "",
        "formations": "",
        "langues": "",
        "loisirs": ""
    }

    current = "contact"

    for line in text.split("\n"):
        clean = line.strip()

        normalized = normalize_title(clean)

        # Si on détecte un vrai titre de section
        if normalized != "contact":
            current = normalized
            continue

        sections[current] += clean + "\n"

    return sections



# ==========================================================
# PARSING DES SECTIONS
# ==========================================================

def parse_contact(text: str) -> Dict[str, Any]:
    result = {
        "nom": None,
        "email": None,
        "telephone": None,
        "adresse": None
    }

    email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if email:
        result["email"] = email.group(0)

    tel = re.search(r"(0|\+33)[\s\d\(\)\.]{8,20}", text)
    if tel:
        result["telephone"] = tel.group(0)

    adr = re.search(r"\d{5}\s+[A-Za-z\- ]+", text)
    if adr:
        result["adresse"] = adr.group(0)

    for line in text.split("\n")[:10]:
        clean = line.strip()

        if any(m in clean.lower() for m in ["analyst", "développeur", "ingénieur", "consultant"]):
            continue

        if re.match(r"^[A-ZÉÈÊÀÂÎÔÙÛ][a-zéèêàâîôùû]+ [A-ZÉÈÊÀÂÎÔÙÛ]+", clean):
            result["nom"] = clean
            break

    
    # Si aucun nom détecté mais initiales présentes
    if result["nom"] is None:
        match = re.search(r"\b[A-Z]{2,4}\b", text)
        if match:
            result["nom"] = match.group(0)

    return result

def parse_competences(text: str) -> List[str]:
    competences = []

    for line in text.split("\n"):
        line = line.strip("-• \t")

        if ":" in line:
            line = line.split(":", 1)[1]

        parts = re.split(r",|/|;", line)

        for p in parts:
            p = p.strip()
            if len(p) > 1:
                competences.append(p)

    return list(dict.fromkeys(competences))


def parse_formations(text: str) -> List[str]:

    formations = []

    pattern_diplome = re.compile(
        r"(19|20)\d{2}\s*[–-]\s*.+",
        re.IGNORECASE
    )

    mots_cles_diplome = [
        "diplôme", "master", "licence", "école",
        "certification", "baccalauréat", "bac",
        "istqb", "scrum", "psm"
    ]

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        # On garde seulement les vraies formations / diplômes
        if any(m in line.lower() for m in mots_cles_diplome):
            formations.append(line)
            continue

        # Années sans mois = plutôt formation
        if pattern_diplome.match(line) and not re.search(
            r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)",
            line.lower()
        ):
            formations.append(line)

    return list(dict.fromkeys(formations))


def parse_experiences(text: str) -> List[str]:

    experiences = []

    pattern_experience = re.compile(
        r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)?\s*"
        r"(19|20)\d{2}.*(–|-).+",
        re.IGNORECASE
    )

    for line in text.split("\n"):
        line = line.strip()

        if pattern_experience.match(line):
            experiences.append(line)

    return experiences

def parse_langues(text: str):

    result = []

    for line in text.split("\n"):
        if "français" in line.lower() or "anglais" in line.lower():
            result.append(line.strip())

    return result

def parse_loisirs(text: str) -> List[str]:
    loisirs = []

    for line in text.split("\n"):
        line = line.strip("-• ")
        if line:
            loisirs.append(line)

    return loisirs


# ==========================================================
# PIPELINE PRINCIPAL
# ==========================================================

def extract_cv_robust(file_path: str) -> Dict[str, Any]:

    logger.info(f"Extraction de: {file_path}")

    raw = extract_text(file_path)
    clean = clean_text(raw)

    sections = find_sections(clean)

    data = {
        "contact": parse_contact(sections.get("contact", "")),
        "competences": parse_competences(sections.get("competences", "")),
        "formations": parse_formations(sections.get("formations", "")),
        "experiences": parse_experiences(sections.get("experiences", "")),
        "langues": parse_langues(sections.get("langues", "")),
        "loisirs": parse_loisirs(sections.get("loisirs", "")),
        "texte_brut": clean
    }

    return data


if __name__ == "__main__":
    import json
    res = extract_cv_robust("test.pdf")
    print(json.dumps(res, indent=2, ensure_ascii=False))
