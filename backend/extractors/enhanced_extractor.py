"""
Extracteur spaCy amélioré utilisant les modèles entraînés.

Ce module:
1. Charge le modèle CV entraîné (NER + TextCat) s'il existe
2. Sinon utilise le modèle fr_core_news_md standard
3. Combine extraction ML + règles heuristiques améliorées
"""

import os
import re
import spacy
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Chemin vers le modèle entraîné (relatif au dossier backend)
TRAINED_MODEL_PATH = Path(__file__).parent.parent / "models" / "cv_pipeline"
BASE_MODEL = "fr_core_news_md"

# Labels NER personnalisés
CUSTOM_NER_LABELS = {
    "PERSON_NAME", "COMPANY", "SCHOOL", "DIPLOMA", 
    "JOB_TITLE", "SKILL", "LANGUAGE", "DATE_RANGE", "LOCATION"
}

# =============================================================================
# DICTIONNAIRES DE RÉFÉRENCE ENRICHIS
# =============================================================================

# Titres de sections à exclure des noms
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
    "activités", "activités extra-scolaires", "hobbies", "centres", "intérêt"
}

# Mots parasites qui ne sont jamais des noms de personnes
NOISE_WORDS = {
    "savoirs", "être", "faire", "savoir", "sens", "détails", "méticuleux",
    "calme", "curiosité", "culturelle", "autonomie", "communication",
    "outils", "informatique", "microsoft", "figma", "salesforce", "git", "jira",
    "python", "java", "javascript", "html", "css", "sql", "agile", "scrum",
    "développeur", "ingénieur", "consultant", "manager", "lead", "chef",
    "stage", "alternance", "projet", "expérience", "formation",
    # Titres de sections courants (avec variantes)
    "compétences", "competences", "competence", "compétence", "techniques",
    "techniqu", "technique", "technologie", "technologies", "professionnelles",
    "personnelles", "langues", "langue", "formations", "expériences",
    "professionnel", "professionnelle", "comportementales", "transversales",
    "environnement", "technique", "logiciels", "logiciel", "certifications",
    "certification", "centres", "intérêt", "intérêts", "loisirs", "hobbies"
}

# Entreprises connues (pour validation ORG)
KNOWN_COMPANIES = {
    "google", "amazon", "microsoft", "apple", "meta", "facebook",
    "sopra steria", "capgemini", "accenture", "atos", "cgi", "thales",
    "orange", "bnp paribas", "société générale", "crédit agricole",
    "airbus", "safran", "dassault", "renault", "peugeot", "total",
    "sncf", "edf", "engie", "bouygues", "vinci", "axa", "allianz"
}

# Écoles/universités connues
KNOWN_SCHOOLS = {
    "polytechnique", "centrale", "mines", "ponts", "supélec", "télécom",
    "hec", "essec", "escp", "em lyon", "edhec", "insead",
    "sorbonne", "paris-saclay", "dauphine", "assas", "panthéon",
    "imt", "insa", "ensam", "ensae", "ensta", "epita", "epitech"
}

# Compétences techniques courantes
TECHNICAL_SKILLS = {
    # Langages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql",
    # Frameworks
    "react", "angular", "vue", "vue.js", "node.js", "django", "flask", "spring",
    "express", ".net", "laravel", "rails", "fastapi",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "gitlab ci", "github actions", "circleci",
    # Bases de données
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
    # Outils
    "git", "jira", "confluence", "notion", "figma", "slack"
}

# =============================================================================
# CHARGEMENT DU MODÈLE
# =============================================================================

_nlp_cache = None

def get_nlp():
    """Charge le modèle spaCy (entraîné ou standard)."""
    global _nlp_cache
    
    if _nlp_cache is not None:
        return _nlp_cache
    
    # Essayer de charger le modèle entraîné
    if TRAINED_MODEL_PATH.exists():
        try:
            _nlp_cache = spacy.load(TRAINED_MODEL_PATH)
            logger.info(f"✓ Modèle CV entraîné chargé: {TRAINED_MODEL_PATH}")
            return _nlp_cache
        except Exception as e:
            logger.warning(f"Erreur chargement modèle entraîné: {e}")
    
    # Fallback vers le modèle standard
    try:
        _nlp_cache = spacy.load(BASE_MODEL)
        logger.info(f"✓ Modèle standard chargé: {BASE_MODEL}")
    except OSError:
        logger.error(f"Modèle {BASE_MODEL} non trouvé. Installation requise.")
        raise
    
    return _nlp_cache


# =============================================================================
# FONCTIONS HEURISTIQUES AMÉLIORÉES
# =============================================================================

def is_valid_person_name(text: str) -> bool:
    """
    Valide si un texte est un nom de personne valide.
    Règles strictes pour éviter les faux positifs.
    """
    text = text.strip()
    
    # Longueur
    if len(text) < 4 or len(text) > 50:
        return False
    
    text_lower = text.lower()
    
    # Exclure les titres de sections
    if text_lower in SECTION_TITLES:
        return False
    
    # Exclure si le texte ressemble à un titre de section fragmenté
    # Ex: "Competences Techniqu Es" → contient "competen" ou "techniqu"
    section_fragments = [
        "competen", "techniqu", "professionn", "personn", "comportem",
        "transvers", "environnem", "certificat", "logiciel", "methodolog",
        "formation", "experience", "langues", "projets", "loisirs",
        "education", "contact", "coordonn", "objectif", "profil"
    ]
    for frag in section_fragments:
        if frag in text_lower:
            return False
    
    # Exclure les mots parasites
    words = set(re.split(r"[\s\-]+", text_lower))
    if words & NOISE_WORDS:
        return False
    
    # Exclure si contient des caractères suspects
    if re.search(r'[@#$%&*=+\[\]{}|\\<>]', text):
        return False
    
    # Exclure les nombres longs
    if re.search(r'\d{3,}', text):
        return False
    
    # Exclure les compétences techniques
    if text_lower in TECHNICAL_SKILLS:
        return False
    
    # Doit contenir 2-4 parties (prénom + nom)
    parts = [p for p in re.split(r"[\s\-]+", text) if p and len(p) > 1]
    if not (2 <= len(parts) <= 4):
        return False
    
    # Vérifier le format des parties
    valid_parts = 0
    for p in parts:
        # Prénom: Capitale + minuscules
        if re.match(r"^[A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ][a-zàâäçéèêëîïôöùûüÿœæ']+$", p):
            valid_parts += 1
        # NOM: TOUT EN MAJUSCULES
        elif re.match(r"^[A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ]{2,}$", p):
            valid_parts += 1
    
    return valid_parts >= 2


def is_valid_company(text: str) -> bool:
    """Valide si un texte est un nom d'entreprise valide."""
    text = text.strip()
    text_lower = text.lower()
    
    if len(text) < 2 or len(text) > 100:
        return False
    
    # Entreprises connues
    if any(comp in text_lower for comp in KNOWN_COMPANIES):
        return True
    
    # Exclure les titres de sections
    if text_lower in SECTION_TITLES:
        return False
    
    # Exclure les patterns numériques
    if re.match(r'^[\d\s\-/]+$', text):
        return False
    
    return True


def is_valid_school(text: str) -> bool:
    """Valide si un texte est un établissement d'enseignement valide."""
    text_lower = text.lower()
    
    # Mots-clés d'écoles
    school_keywords = ["université", "école", "institut", "iut", "lycée", "college"]
    if any(kw in text_lower for kw in school_keywords):
        return True
    
    # Écoles connues
    if any(school in text_lower for school in KNOWN_SCHOOLS):
        return True
    
    return False


def extract_name_from_email(email: str) -> Optional[str]:
    """
    Extrait le nom depuis une adresse email.
    Ex: oussama.bennouri@gmail.com → Oussama BENNOURI
    """
    if not email or '@' not in email:
        return None
    
    local_part = email.split('@')[0]
    
    # Patterns courants: prenom.nom, prenom_nom, prenom-nom
    # Essayer d'abord le point, puis underscore, puis tiret
    separators = ['.', '_']
    
    for sep in separators:
        if sep in local_part:
            parts = local_part.split(sep)
            if len(parts) >= 2:
                # Gérer les prénoms composés (jean-pierre.martin)
                prenom_parts = parts[0].replace('-', ' ').split()
                prenom = '-'.join(p.capitalize() for p in prenom_parts) if '-' in parts[0] else parts[0].capitalize()
                nom = parts[-1].upper()  # Prendre la dernière partie comme nom
                
                # Valider que ce sont des parties valides (lettres uniquement, avec tiret pour prénom)
                if re.match(r'^[a-zA-ZÀ-ÿ\-]+$', prenom) and re.match(r'^[a-zA-ZÀ-ÿ]+$', nom):
                    if len(prenom) >= 2 and len(nom) >= 2:
                        return f"{prenom} {nom}"
    
    return None


def extract_name_from_header(text: str) -> Optional[str]:
    """
    Extrait le nom du candidat depuis l'en-tête du CV.
    Utilise des heuristiques strictes.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()][:10]
    
    for line in lines:
        # Nettoyer la ligne
        line_clean = line.strip(" •\t·-–—")
        
        # Ignorer les lignes trop longues ou trop courtes
        if len(line_clean) < 4 or len(line_clean) > 50:
            continue
        
        # Ignorer si c'est un titre de section
        if line_clean.lower() in SECTION_TITLES:
            continue
        
        # Ignorer si contient email/téléphone
        if re.search(r'[@\d]{5,}', line_clean):
            continue
        
        # Ignorer si c'est un titre de poste
        if re.search(r'\b(développeur|ingénieur|consultant|manager|chef|lead)\b', 
                     line_clean, re.IGNORECASE):
            continue
        
        # Valider comme nom
        if is_valid_person_name(line_clean):
            return clean_name(line_clean)
    
    return None


def clean_name(text: str) -> str:
    """Nettoie un nom extrait."""
    # Supprimer les titres de poste
    text = re.sub(
        r'\b(?:développeur|developpeur|developer|ingénieur|ingenieur|consultant|'
        r'manager|chef|full\s*stack|data|web|senior|junior|lead|stagiaire|alternant)\b.*',
        '', text, flags=re.IGNORECASE
    )
    
    # Nettoyer la ponctuation finale
    text = re.sub(r'\s*[,\-:]+\s*$', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_skills_from_text(text: str) -> List[str]:
    """Extrait les compétences techniques du texte."""
    skills = set()
    text_lower = text.lower()
    
    # Rechercher les compétences connues
    for skill in TECHNICAL_SKILLS:
        # Pattern avec limites de mots
        pattern = rf'\b{re.escape(skill)}\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            skills.add(skill.upper() if len(skill) <= 3 else skill.title())
    
    return sorted(skills)


def classify_section(text: str, nlp=None) -> Tuple[str, float]:
    """
    Classifie une section de CV.
    Retourne (catégorie, score de confiance).
    """
    if nlp is None:
        nlp = get_nlp()
    
    # Si le modèle a TextCat, l'utiliser
    doc = nlp(text)
    if doc.cats:
        sorted_cats = sorted(doc.cats.items(), key=lambda x: x[1], reverse=True)
        return sorted_cats[0]
    
    # Sinon, utiliser des règles
    text_lower = text.lower()
    
    section_keywords = {
        "EDUCATION": ["formation", "diplôme", "université", "école", "master", "licence", "bac"],
        "EXPERIENCE": ["expérience", "poste", "entreprise", "stage", "alternance", "cdi", "cdd"],
        "SKILLS": ["compétences", "skills", "outils", "technologies", "langages"],
        "LANGUAGES": ["langues", "français", "anglais", "espagnol", "allemand"],
        "PROJECTS": ["projets", "projet", "réalisations"],
        "CERTIFICATIONS": ["certifications", "certification", "certificat"],
        "INTERESTS": ["loisirs", "intérêts", "hobbies", "passions"]
    }
    
    for category, keywords in section_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return (category, 0.8)
    
    return ("OTHER", 0.5)


# =============================================================================
# FONCTION PRINCIPALE D'EXTRACTION
# =============================================================================

def extraire_entites_ameliore(texte: str) -> Dict[str, Any]:
    """
    Extraction d'entités améliorée combinant ML et règles.
    
    Retourne un dictionnaire avec:
    - noms: Liste des noms détectés
    - organisations: Entreprises
    - ecoles: Établissements d'enseignement
    - postes: Titres de poste
    - competences: Compétences techniques
    - langues: Langues parlées
    - lieux: Localisations
    - dates: Dates et périodes
    """
    nlp = get_nlp()
    doc = nlp(texte)
    
    entites = {
        "noms": [],
        "organisations": [],
        "ecoles": [],
        "postes": [],
        "competences": [],
        "langues": [],
        "lieux": [],
        "dates": []
    }
    
    # =========================================================================
    # PHASE 1: Extraction via modèle spaCy (standard ou entraîné)
    # =========================================================================
    
    for ent in doc.ents:
        val = ent.text.strip()
        if not val or len(val) < 2:
            continue
        
        label = ent.label_
        
        # Labels personnalisés (si modèle entraîné)
        if label == "PERSON_NAME":
            if is_valid_person_name(val):
                entites["noms"].append(clean_name(val))
        
        elif label == "COMPANY":
            if is_valid_company(val):
                entites["organisations"].append(val)
        
        elif label == "SCHOOL":
            entites["ecoles"].append(val)
        
        elif label == "JOB_TITLE":
            entites["postes"].append(val)
        
        elif label == "SKILL":
            entites["competences"].append(val)
        
        elif label == "LANGUAGE":
            entites["langues"].append(val)
        
        elif label == "LOCATION":
            entites["lieux"].append(val)
        
        elif label == "DATE_RANGE":
            entites["dates"].append(val)
        
        # Labels spaCy standard
        elif label == "PER":
            if is_valid_person_name(val):
                entites["noms"].append(clean_name(val))
        
        elif label == "ORG":
            if is_valid_company(val):
                if is_valid_school(val):
                    entites["ecoles"].append(val)
                else:
                    entites["organisations"].append(val)
        
        elif label in ("LOC", "GPE"):
            entites["lieux"].append(val)
        
        elif label == "DATE":
            entites["dates"].append(val)
    
    # =========================================================================
    # PHASE 2: Extraction heuristique (fallback et enrichissement)
    # =========================================================================
    
    # Nom en en-tête si non trouvé
    if not entites["noms"]:
        name = extract_name_from_header(texte)
        if name:
            entites["noms"].append(name)
    
    # Fallback: extraire le nom depuis l'email si toujours pas de nom
    if not entites["noms"]:
        # Chercher un email dans le texte
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', texte)
        if email_match:
            name_from_email = extract_name_from_email(email_match.group())
            if name_from_email:
                entites["noms"].append(name_from_email)
    
    # Compétences techniques
    skills = extract_skills_from_text(texte)
    for skill in skills:
        if skill not in entites["competences"]:
            entites["competences"].append(skill)
    
    # Extraction regex pour organisations
    org_patterns = [
        r'\b(Sopra\s*Steria|Capgemini|Accenture|Atos|CGI|Thales|Orange|BNP|SNCF)\b',
        r'\bchez\s+([A-Z][A-Za-zÀ-ÿ\s&]+?)(?:\s*[\(\-,]|\s*$)',
        r'\b(?:chez|at|@)\s+([A-Z][A-Za-zÀ-ÿ0-9\s&]+?)(?:\s*[\(\-,\n])',
    ]
    
    for pattern in org_patterns:
        for m in re.finditer(pattern, texte, re.IGNORECASE):
            org = m.group(1).strip() if m.lastindex else m.group(0).strip()
            if is_valid_company(org) and org not in entites["organisations"]:
                entites["organisations"].append(org)
    
    # Extraction regex pour écoles
    school_patterns = [
        r'(Université\s+(?:de\s+)?[A-Za-zÀ-ÿ\s\-\']+)',
        r'(École\s+(?:Nationale\s+)?(?:Supérieure\s+)?[A-Za-zÀ-ÿ\s\-\']+)',
        r'(IMT\s+[A-Za-zÀ-ÿ\s\-]+)',
        r'(IUT\s+[A-Za-zÀ-ÿ\s\-]+)',
    ]
    
    for pattern in school_patterns:
        for m in re.finditer(pattern, texte, re.IGNORECASE):
            school = m.group(1).strip()
            if school and school not in entites["ecoles"]:
                entites["ecoles"].append(school)
    
    # Extraction regex pour dates
    date_patterns = [
        r'\b(\d{4})\s*[-–—]\s*(\d{4}|[Pp]résent|[Aa]ctuel)',
        r'\b([Jj]anvier|[Ff]évrier|[Mm]ars|[Aa]vril|[Mm]ai|[Jj]uin|'
        r'[Jj]uillet|[Aa]oût|[Ss]eptembre|[Oo]ctobre|[Nn]ovembre|[Dd]écembre)'
        r'\s+\d{4}\s*[-–—]\s*(?:[A-Za-zé]+\s+\d{4}|[Pp]résent)',
    ]
    
    for pattern in date_patterns:
        for m in re.finditer(pattern, texte):
            date_str = m.group(0).strip()
            if date_str not in entites["dates"]:
                entites["dates"].append(date_str)
    
    # =========================================================================
    # PHASE 3: Nettoyage et dédoublonnage
    # =========================================================================
    
    for key in entites:
        seen = set()
        unique = []
        for item in entites[key]:
            if not item:
                continue
            item = re.sub(r'\s+', ' ', item).strip()
            item_lower = item.lower()
            
            # Exclure les titres de sections
            if item_lower in SECTION_TITLES:
                continue
            
            if item_lower not in seen:
                seen.add(item_lower)
                unique.append(item)
        
        entites[key] = unique
    
    return entites


# =============================================================================
# COMPATIBILITÉ AVEC L'ANCIEN EXTRACTEUR
# =============================================================================

def extraire_entites(texte: str) -> Dict[str, List[str]]:
    """
    Interface de compatibilité avec l'ancien extracteur.
    Utilisé par section_classifier.py
    """
    result = extraire_entites_ameliore(texte)
    
    # Fusionner écoles dans organisations pour compatibilité
    organisations = result.get("organisations", []) + result.get("ecoles", [])
    
    return {
        "noms": result.get("noms", []),
        "organisations": organisations,
        "lieux": result.get("lieux", []),
        "dates": result.get("dates", []),
        "competences": result.get("competences", []),
        "langues": result.get("langues", [])
    }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    test_cv = """
Marie DUPONT
06 12 34 56 78 | marie.dupont@gmail.com
15 rue des Lilas, 75001 Paris

PROFIL
Développeuse Full Stack passionnée avec 5 ans d'expérience.

FORMATION
2018-2020: Master Informatique - Université Paris-Saclay
2015-2018: Licence Informatique - Université de Lyon

EXPÉRIENCE PROFESSIONNELLE
2020-2023: Développeur Python Senior chez Google
- Développement d'APIs REST avec Django
- Mise en place CI/CD avec GitLab

2018-2020: Stage Développeur chez Capgemini
- Développement frontend React

COMPÉTENCES
Python, Java, JavaScript, React, Django, Docker, Kubernetes, AWS, Git

LANGUES
Français (natif), Anglais (courant), Espagnol (B1)
"""
    
    print("=" * 60)
    print("TEST EXTRACTEUR AMÉLIORÉ")
    print("=" * 60)
    
    result = extraire_entites_ameliore(test_cv)
    
    for key, values in result.items():
        if values:
            print(f"\n{key.upper()}:")
            for v in values:
                print(f"  - {v}")
