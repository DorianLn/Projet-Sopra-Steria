# backend/extractors/spacy_extractor.py
import spacy
import re
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chemin vers le modèle entraîné
TRAINED_MODEL_PATH = Path(__file__).parent.parent / "models" / "cv_pipeline"
BASE_MODEL = "fr_core_news_md"

SECTION_TITLES = {
    "langues", "langue", "compétences", "competences", "competence", "compétence",
    "formations", "formation", "expérience", "experience", "expériences", "experiences",
    "profil", "contact", "projets", "projet", "certification", "certifications",
    "loisirs", "centres d'intérêt", "divers", "informations", "personnelles",
    "coordonnées", "coordonnees", "objectif", "résumé", "resume", "summary",
    "skills", "education", "work experience", "professional experience",
    "savoirs", "savoir", "savoir-être", "savoirs-être", "savoir-faire", "savoirs-faire",
    "soft skills", "hard skills", "compétences techniques", "compétences comportementales",
    "outils", "outils informatiques", "technologies", "méthodologies",
    "activités", "activités extra-scolaires", "hobbies", "centres", "intérêt",
    "passions", "voyages", "curiosité", "curiosité culturelle"
}

NOISE_WORDS = {
    "savoirs", "être", "faire", "savoir", "sens", "détails", "méticuleux",
    "calme", "curiosité", "culturelle", "autonomie", "communication",
    "outils", "informatique", "microsoft", "figma", "salesforce", "git", "jira",
    "plotly", "pandas", "python", "java", "javascript", "html", "css", "sql",
    "agile", "scrum", "api", "rest", "analyse", "données", "data",
    "compétences", "competences", "competence", "compétence",
    "techniques", "technique", "technologie", "technologies",
    "professionnelles", "professionnelle", "professionnel",
    "personnelles", "personnelle", "personnel",
    "environnement", "méthodologies", "méthodologie",
    "comportementales", "comportementale", "transversales", "transversale"
}

SECTION_FRAGMENTS = {
    "competen", "techniqu", "professionn", "personn", "comportem",
    "transvers", "environnem", "certificat", "logiciel", "methodolog",
    "formation", "experience", "langues", "projets", "loisirs"
}

POSTE_KEYWORDS = {
    "développeur", "developpeur", "developer", "ingénieur", "ingenieur", "engineer",
    "consultant", "manager", "chef", "responsable", "directeur", "analyste",
    "technicien", "architecte", "lead", "senior", "junior", "stagiaire", "alternant",
    "full stack", "fullstack", "frontend", "backend", "devops", "data", "web",
    "mobile", "software", "project", "product", "scrum", "agile"
}

SKILL_CATEGORIES = {
    "programmation": {"python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "rust", "php", "ruby", "scala"},
    "frameworks": {"react", "angular", "vue", "django", "flask", "spring", "laravel", "rails", "fastapi", "node.js", "node"},
    "bases_de_donnees": {"mysql", "postgresql", "mongodb", "redis", "oracle", "sql server", "cassandra", "elasticsearch"},
    "devops_cloud": {"docker", "kubernetes", "terraform", "ansible", "jenkins", "aws", "azure", "gcp"},
    "outils": {"git", "github", "gitlab", "jira", "confluence", "notion", "figma", "slack"}
}

FONCTIONNEL_KEYWORDS = {
    "agile", "scrum", "kanban", "safe",
    "gestion", "management", "leadership",
    "communication", "organisation",
    "travail en équipe", "relation client",
    "analyse", "méthodologie", "pilotage",
    "gestion de projet", "coordination",
    "résolution de problèmes"
}

def separer_competences(competences_list: list[str]) -> dict:
    """
    Sépare les compétences en techniques et fonctionnelles
    """

    competences_fonctionnelles = []
    competences_techniques = []

    for comp in competences_list:
        comp_lower = comp.lower()

        if any(k in comp_lower for k in FONCTIONNEL_KEYWORDS):
            competences_fonctionnelles.append(comp)
        else:
            competences_techniques.append(comp)

    return {
        "techniques": regrouper_competences(competences_techniques),
        "fonctionnelles": list(dict.fromkeys(competences_fonctionnelles))
    }

def normalize_skill(s: str) -> str:
    return re.sub(r'[^a-z0-9+#\.]', '', s.lower())

def regrouper_competences(skills: list[str]) -> dict:
    grouped = {cat: [] for cat in SKILL_CATEGORIES}
    grouped["autres"] = []

    for skill in skills:
        s_norm = normalize_skill(skill)
        found = False

        for cat, values in SKILL_CATEGORIES.items():
            for v in values:
                v_norm = normalize_skill(v)
                if v_norm in s_norm or s_norm in v_norm:
                    grouped[cat].append(skill)
                    found = True
                    break
            if found:
                break

        if not found:
            grouped["autres"].append(skill)

    for cat in grouped:
        grouped[cat] = list(dict.fromkeys(grouped[cat]))

    return grouped

def load_spacy_model():
    if TRAINED_MODEL_PATH.exists():
        try:
            logger.info(f"Chargement du modèle entraîné depuis: {TRAINED_MODEL_PATH}")
            model = spacy.load(str(TRAINED_MODEL_PATH))
            logger.info("✓ Modèle entraîné chargé avec succès")
            return model, True
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du modèle entraîné: {e}")

    logger.info(f"Chargement du modèle de base: {BASE_MODEL}")
    return spacy.load(BASE_MODEL), False

nlp, IS_TRAINED_MODEL = load_spacy_model()

def extraire_entites(texte: str) -> dict:
    doc = nlp(texte)

    entites = {
        "noms": [],
        "organisations": [],
        "lieux": [],
        "dates": [],
        "competences": [],
        "langues": [],
        "diplomes": [],
        "ecoles": [],
        "postes": []
    }

    for ent in doc.ents:
        val = ent.text.strip()
        if not val or len(val) < 2:
            continue

        label = ent.label_
        val_lower = val.lower()

        if label == "SKILL":
            if val_lower not in SECTION_TITLES:
                entites["competences"].append(val)

        elif label == "LANGUAGE":
            entites["langues"].append(val.capitalize())

        elif label == "COMPANY":
            entites["organisations"].append(val)

        elif label == "SCHOOL":
            entites["ecoles"].append(val)

        elif label == "DIPLOMA":
            entites["diplomes"].append(val)

        elif label == "JOB_TITLE":
            entites["postes"].append(val)

        elif label == "DATE_RANGE":
            entites["dates"].append(val)

    for k in entites:
        entites[k] = list(dict.fromkeys(entites[k]))

    entites["competences_structurees"] = separer_competences(entites["competences"])

    return entites
