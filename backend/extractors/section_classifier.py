import re
import sys
import os
from typing import List, Optional, Tuple
import dateparser
from rich.console import Console
from rich.table import Table
import json
from datetime import datetime

# Import adaptatif pour spacy_extractor
try:
    from extractors.spacy_extractor import extraire_entites, classifier_section_texte
except ImportError:
    try:
        from .spacy_extractor import extraire_entites, classifier_section_texte
    except ImportError:
        from spacy_extractor import extraire_entites, classifier_section_texte

console = Console()

# ---------------------
# 0️ Mots-clés enrichis
# ---------------------
FORMATION_KEYWORDS = [
    "université", "universite", "école", "ecole", "diplôme", "diplome",
    "master", "licence", "bachelor", "ingénieur", "ingenieur", "iut",
    "bts", "dut", "bac", "baccalauréat", "doctorat", "phd", "mba",
    "formation", "certificat", "diplômé", "diplome", "cursus", "études"
]
EXPERIENCE_KEYWORDS = [
    "stage", "alternance", "développeur", "developpeur", "full stack",
    "chef de projet", "consultant", "expérience", "experience",
    "ingénieur", "ingenieur", "manager", "stagiaire", "mission",
    "cdi", "cdd", "freelance", "indépendant", "contrat", "poste",
    "employé", "responsable", "directeur", "analyste", "technicien",
    "architecte", "lead", "senior", "junior"
]
STOP_ORG = {
    "assoc", "association", "leadership", "club", "projets", "projet", 
    "volontariat", "bénévolat", "loisirs", "hobbies", "centres", "intérêt",
    # Outils et technologies (PAS des entreprises)
    "plotly", "pandas", "python", "java", "javascript", "html", "css", "sql",
    "git", "github", "jira", "figma", "salesforce", "docker", "kubernetes",
    "react", "angular", "vue", "flask", "django", "spring", "api",
    # Mots génériques
    "microsoft", "outils", "informatique", "outils informatique", "outils microsoft",
    # Sections parasites
    "savoirs", "savoir", "savoir-être", "savoirs-être", "soft skills", "hard skills",
    "compétences", "competences", "compétence", "curiosité", "curiosité culturelle",
    "sens", "détails", "méticuleux", "calme", "autonomie",
    # Pays/Villes (pas des entreprises)
    "allemagne", "france", "espagne", "italie", "portugal", "belgique",
    "paris", "lyon", "marseille", "toulouse", "bordeaux", "boston",
    # Mots de contexte
    "expériences", "experience", "formations", "formation", "langues", "langue"
}

COMPETENCE_KEYWORDS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "docker", "kubernetes", "sql", "mysql", "postgresql", "mongodb",
    "aws", "azure", "gcp", "git", "github", "gitlab", "html", "css",
    "flask", "django", "fastapi", "spring", "linux", "node", "nodejs",
    "api", "rest", "graphql", "ci/cd", "devops", "agile", "scrum",
    "cloud", "communication", "gestion de projet", "leadership", "autonomie",
    "travail en équipe", "résolution de problèmes", "analyse", "c++", "c#",
    ".net", "php", "ruby", "go", "rust", "swift", "kotlin", "scala"
]
LANGUES_KEYWORDS = [
    "français", "francais", "anglais", "espagnol", "allemand", "italien",
    "portugais", "chinois", "mandarin", "japonais", "arabe", "russe",
    "néerlandais", "polonais", "coréen", "hindi"
]

DATE_REGEXES = [
    r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
    r'\b\d{1,2}[\/\-]\d{4}\b',
    r'\b(?:19|20)\d{2}\b',
    r'\b(?:Janvier|Février|Fevrier|Mars|Avril|Mai|Juin|Juillet|Août|Aout|Septembre|Octobre|Novembre|Décembre)\s+\d{4}\b',
    r'\b(?:\d{4})\s*[-–—]\s*(?:\d{4}|[Pp]résent|[Aa]ctuel(?:lement)?|[Aa]ujourd\'?hui)\b'
]

# ---------------------
# 1️ Extraction de base
# ---------------------
def extraire_competences_langues(texte):
    texte_min = texte.lower()
    competences = []
    langues = []
    
    for m in COMPETENCE_KEYWORDS:
        if re.search(rf"\b{re.escape(m)}\b", texte_min):
            comp = m.title() if len(m) > 3 else m.upper()
            if comp not in competences:
                competences.append(comp)
    
    for m in LANGUES_KEYWORDS:
        if re.search(rf"\b{re.escape(m)}\b", texte_min):
            lang = m.capitalize()
            if lang not in langues:
                langues.append(lang)
    
    return competences, langues


def extract_date_spans(text: str):
    """
    Extrait toutes les dates présentes dans le texte (simples ou plages).
    Renvoie une liste de tuples (brut, start, end, normalisé)
    """
    spans = []
    for rx in DATE_REGEXES:
        for m in re.finditer(rx, text, flags=re.IGNORECASE):
            raw = m.group(0).strip()
            start, end = m.start(), m.end()

            #  1. Détection directe des plages de dates
            if re.match(r"^(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}$", raw):
                spans.append((raw, start, end, raw))
                continue

            #  2. Filtrage des faux positifs (code postal, etc.)
            window = text[max(0, start - 8):min(len(text), end + 8)]
            if re.search(r"\b\d{5}\b", window) and re.fullmatch(r"(?:19|20)\d{2}", raw):
                continue

            #  3. Parsing “humain”
            parsed = None
            try:
                dp = dateparser.parse(raw, languages=['fr'])
                if dp:
                    parsed = dp.date().isoformat()

                    #  Filtrer les dates du jour (erreur fréquente de dateparser)
                    if parsed.endswith("-11-12") or parsed.endswith("-11-11"):
                        continue
            except Exception:
                parsed = None

            spans.append((raw, start, end, parsed or raw))

    #  4. Tri + suppression doublons
    spans_sorted = sorted(spans, key=lambda x: x[1])
    unique, seen = [], set()
    for s in spans_sorted:
        if s[1] not in seen:
            unique.append(s)
            seen.add(s[1])
    return unique


def find_org_positions(org: str, text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in re.finditer(re.escape(org), text, flags=re.IGNORECASE)]


def find_closest_date_by_char(org: str, text: str, date_spans: List[Tuple[str, int, int, str]]) -> Optional[str]:
    org_positions = find_org_positions(org, text)
    if not org_positions:
        return None
    best, best_dist = None, 1200
    for (o_start, o_end) in org_positions:
        for raw, d_start, d_end, parsed in date_spans:
            dist = abs(((o_start + o_end) / 2) - ((d_start + d_end) / 2))
            if dist < best_dist:
                best_dist, best = dist, (parsed or raw)
    return best if best_dist < 1200 else None


# ---------------------
# 2️ Nettoyage
# ---------------------
def nettoyer_nom_organisation(org: str) -> str:
    org = re.sub(r"(?i)(entreprise|projets?|compétences?|competences?|stage|formation)[:\s-]*", "", org)
    org = re.sub(r"\s+", " ", org)
    return org.strip(" :-\n\t")


def is_formation(org_text: str, context_text: str = "") -> bool:
    ol = org_text.lower()
    if any(k in ol for k in FORMATION_KEYWORDS) or any(k in context_text.lower() for k in FORMATION_KEYWORDS):
        return True
    return "univ" in ol or "univers" in ol


def is_valid_school(name: str) -> bool:
    """Vérifie si le nom ressemble à un vrai établissement de formation"""
    name_lower = name.lower().strip()
    
    # Trop court pour être un établissement
    if len(name_lower) < 4:
        return False
    
    # Mots parasites qui ne sont pas des écoles
    INVALID_SCHOOL_WORDS = {
        "culturelle", "culturelle /", "curiosité", "autonomie", "communication",
        "savoir", "savoirs", "être", "faire", "soft", "hard", "skills",
        "sens", "détails", "détail", "méticuleux", "calme", "rigueur",
        # Loisirs / Sports
        "calisthénie", "sport", "musique", "lecture", "voyage", "voyages",
        # Mots techniques
        "serveur", "système", "jeu", "rush", "implémentation", "interaction",
        # Langues (pas des écoles)
        "français", "anglais", "allemand", "espagnol", "italien",
    }
    
    if name_lower in INVALID_SCHOOL_WORDS:
        return False
    
    # Contient un slash ou des caractères suspects
    if "/" in name and "iut" not in name_lower:
        return False
    
    # Un établissement valide contient souvent des mots-clés
    valid_school_keywords = {"école", "ecole", "université", "universite", "iut", 
                             "bts", "lycée", "lycee", "college", "institut",
                             "epita", "epitech", "hec", "essec", "polytechnique",
                             "centrale", "supérieur", "superieur", "nationale"}
    
    if any(kw in name_lower for kw in valid_school_keywords):
        return True
    
    # Accepter les noms propres avec majuscule (ex: "Lycée Hoche")
    words = name.split()
    if len(words) >= 2 and words[0][0].isupper():
        return True
    
    return False


def nettoyer_organisations(entites_org):
    nettoyees = []
    for org in entites_org:
        org_clean = re.sub(r'\s+', ' ', org.strip())
        morceaux = re.split(r'[\-–—](?!\s*(?:19|20)\d{2})', org_clean)
        for part in morceaux:
            part = part.strip(" -–—.,;")
            if len(part) > 2 and part.lower() not in STOP_ORG:
                nettoyees.append(part)
    return list(dict.fromkeys(nettoyees))


# ---------------------
# 3️ Analyse de sections additionnelles
# ---------------------
NIVEAUX = {
    "natif": "C2", "bilingue": "C2", "courant": "C1", "professionnel": "C1",
    "intermédiaire": "B2", "débutant": "A2", "notions": "A1"
}
LANG_LIST = ["français", "francais", "anglais", "espagnol", "allemand", "italien", "portugais", "arabe"]

def parse_section_langues(texte):
    m = re.search(r"(?is)\bLangues?\b\s*[:\-\n]*(.+?)(?:\n\s*(?:Compétences?|Formations?|Expériences?|Certifications?)\b|$)", texte)
    if not m:
        return []
    bloc = m.group(1)
    items = re.split(r"[•\-\u2022,;/\n]+", bloc)
    out = []
    for it in items:
        t = it.strip()
        if not t:
            continue
        low = t.lower()
        if any(l in low for l in LANG_LIST):
            lvl = next((v for k, v in NIVEAUX.items() if re.search(rf"\b{k}\b", low)), None)
            out.append(t if not lvl else f"{t} ({lvl})")
    return list(dict.fromkeys(out))

def parse_section_competences(texte):
    m = re.search(r"(?is)\bCompétences?\b\s*[:\-\n]*(.+?)(?:\n\s*(?:Langues?|Formations?|Expériences?|Certifications?)\b|$)", texte)
    if not m:
        return []
    bloc = m.group(1)
    items = re.split(r"[•\-\u2022,;/\n]+", bloc)
    out = []
    for it in items:
        t = re.sub(r"^[\-\•\d]+\s*", "", it.strip().lower())
        if 2 <= len(t) <= 40 and not re.search(r"\d", t) and not re.search(r"principale", t, re.IGNORECASE):
            out.append(t.capitalize())
    return list(dict.fromkeys(out))

def parse_section_projets(texte):
    matches = re.findall(r"(?:Projets?|Réalisations?)[:\-\n]+([\s\S]+?)(?=\n[A-ZÉÈ]|$)", texte, re.IGNORECASE)
    if not matches:
        return []
    bloc = matches[0]
    items = re.split(r"[•\-\u2022,;\n]+", bloc)
    projets = [i.strip(" .") for i in items if 3 < len(i.strip()) < 80]
    return list(dict.fromkeys(projets))

def parse_section_certifications(texte):
    matches = re.findall(r"(?:Certifications?|Certif)[\s:]+(.+?)(?=\n[A-ZÉÈ]|$)", texte, re.IGNORECASE)
    if not matches:
        return []
    items = re.split(r"[•\-\u2022,;\n]+", matches[0])
    certifs = [i.strip() for i in items if len(i.strip()) > 3]
    return list(dict.fromkeys(certifs))

def parse_section_loisirs(texte):
    matches = re.findall(r"(?:Loisirs?|Centres d’intérêt)[:\-\s]+(.+?)(?=\n[A-ZÉÈ]|$)", texte, re.IGNORECASE)
    if not matches:
        return []
    items = re.split(r"[,;/]+", matches[0])
    return [i.strip() for i in items if len(i.strip()) > 2]

def parse_disponibilite(texte):
    m = re.search(r"Disponible\s+(?:à partir de|dès)?\s*(.+?)(?:\.|\n|$)", texte, re.IGNORECASE)
    return m.group(1).strip() if m else None


# ---------------------
# Extraction du NOM robuste
# ---------------------
NAME_EXCLUSIONS = {
    "savoirs", "savoir", "être", "faire", "soft", "hard", "skills", "compétences",
    "expériences", "formations", "langues", "projets", "certifications", "loisirs",
    "contact", "profil", "objectif", "résumé", "cv", "curriculum", "vitae",
    "outils", "informatique", "microsoft", "figma", "git", "jira",
    "développeur", "developer", "ingénieur", "consultant", "manager", "chef",
    "sens", "détails", "méticuleux", "calme", "curiosité", "culturelle", "autonomie",
    "activités", "extra", "scolaires", "voyages", "passions", "hobbies",
    # Mots de sections techniques
    "compétences", "competences", "techniques", "technique", "techniqu",
    "professionnelles", "professionnelle", "personnelles", "personnelle",
    "environnement", "méthodologies", "technologies", "comportementales"
}

# Fragments de titres de sections (pour détecter "Competences Techniqu Es")
SECTION_FRAGMENTS = {
    "competen", "techniqu", "professionn", "personn", "comportem",
    "transvers", "environnem", "certificat", "logiciel", "methodolog"
}

# Mots d'adresse à détecter
ADRESSE_KEYWORDS = [
    "rue", "avenue", "boulevard", "place", "chemin", "impasse", "allée", "allee",
    "cour", "quai", "passage", "square", "route", "voie"
]

def extract_name_from_header(texte: str) -> Optional[str]:
    """
    Extrait le nom depuis l'en-tête du CV (généralement les 5-10 premières lignes).
    Le nom est souvent la première ligne non vide qui ressemble à "Prénom NOM".
    """
    lines = [l.strip() for l in texte.split('\n') if l.strip()][:15]
    
    # ÉTAPE 1: Trouver tous les noms qui apparaissent dans les adresses (à exclure)
    noms_dans_adresse = set()
    pattern_rue_nom = r'(?:rue|avenue|boulevard|place|chemin|impasse|allée|allee|passage|quai|square|route)\s+([A-Za-zéèêëîïôöûüçÀ-ÿ\-]+(?:\s+[A-Za-zéèêëîïôöûüçÀ-ÿ\-]+)*)'
    for match in re.finditer(pattern_rue_nom, texte, re.IGNORECASE):
        nom_rue = match.group(1).strip().lower()
        noms_dans_adresse.add(nom_rue)
        # Ajouter aussi chaque mot individuellement
        for word in nom_rue.split():
            if len(word) > 2:
                noms_dans_adresse.add(word)
    
    for line in lines:
        line_clean = line.strip(" \t\n\r\u2022\u2023\u25cf\u25e6\u2013\u2014-")
        
        # Ignorer les lignes trop courtes ou trop longues
        if len(line_clean) < 4 or len(line_clean) > 45:
            continue
        
        # Ignorer si contient email, téléphone, adresse
        if re.search(r'[@\d]{5,}', line_clean):
            continue
        if re.search(r'\d{5}', line_clean):  # Code postal
            continue
        if re.search(r'\+?\d[\d\s\(\)\-]{8,}', line_clean):  # Téléphone
            continue
        
        # Ignorer si contient un mot d'adresse
        if any(kw in line_clean.lower() for kw in ADRESSE_KEYWORDS):
            continue
        
        line_lower = line_clean.lower()
        
        # Ignorer si c'est un titre de section
        if any(excl in line_lower for excl in NAME_EXCLUSIONS):
            continue
        
        # IMPORTANT: Ignorer si contient un fragment de titre de section
        if any(frag in line_lower for frag in SECTION_FRAGMENTS):
            continue
        
        # Ignorer si c'est une section connue
        if re.match(r'^(expériences?|formations?|compétences?|langues?|projets?|contact|profil)\s*[:.]?$', line_lower):
            continue
        
        # Pattern : "Prénom NOM" ou "Prénom Prénom2 NOM"
        # Prénom = Capitale + minuscules, NOM = tout en majuscules ou normale
        if re.match(r'^[A-ZÀ-Ü][a-zà-ÿ]+(?:\s+[A-ZÀ-Ü][a-zà-ÿ]+)*(?:\s+[A-ZÀ-Ü][A-ZÀ-Üa-zà-ÿ]+)+$', line_clean):
            # Vérifier que les mots ne sont pas des exclusions
            words = line_clean.split()
            if all(w.lower() not in NAME_EXCLUSIONS for w in words):
                if len(words) >= 2 and len(words) <= 4:
                    # VÉRIFICATION CROISÉE: rejeter si ce nom apparaît dans une adresse
                    nom_candidat = line_clean.lower()
                    if nom_candidat not in noms_dans_adresse:
                        # Vérifier aussi que les mots individuels ne sont pas dans les noms de rue
                        if not all(w.lower() in noms_dans_adresse for w in words):
                            return line_clean
        
        # Pattern alternatif: "PRENOM NOM" tout en majuscules
        if re.match(r'^[A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)+$', line_clean):
            words = line_clean.split()
            if all(w.lower() not in NAME_EXCLUSIONS for w in words):
                if len(words) >= 2 and len(words) <= 4:
                    nom_candidat = line_clean.lower()
                    # VÉRIFICATION CROISÉE
                    if nom_candidat not in noms_dans_adresse:
                        if not all(w.lower() in noms_dans_adresse for w in words):
                            # Formatter: Prénom Nom
                            return ' '.join(w.capitalize() for w in words)
    
    # Deuxième passe: chercher "Nom : XXX" ou pattern flexible
    for line in lines[:10]:
        m = re.search(r'(?:Nom|Name)\s*[:\-]\s*([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)+)', line, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            words = candidate.split()
            if all(w.lower() not in NAME_EXCLUSIONS for w in words):
                # Vérification croisée avec adresse
                if candidate.lower() not in noms_dans_adresse:
                    if not all(w.lower() in noms_dans_adresse for w in words):
                        return candidate
    
    # Troisième passe: extraire depuis l'email
    email_match = re.search(r'([a-zA-Z]+)[._]([a-zA-Z]+)@', texte)
    if email_match:
        prenom = email_match.group(1).capitalize()
        nom = email_match.group(2).capitalize()
        if len(prenom) > 1 and len(nom) > 1:
            return f"{prenom} {nom}"
    
    return None


# ---------------------
# 4️ Classif formation/exp avec poste amélioré
# ---------------------
POSTE_PATTERNS = [
    r"(développeur\s*(?:web|mobile|full[\s\-]?stack|front[\s\-]?end|back[\s\-]?end|logiciel)?(?:\s+[A-Za-z]+){0,2})",
    r"(developpeur\s*(?:web|mobile|full[\s\-]?stack|front[\s\-]?end|back[\s\-]?end|logiciel)?(?:\s+[A-Za-z]+){0,2})",
    r"(ingénieur\s*(?:études|développement|logiciel|système|réseau|data|devops)?(?:\s+[A-Za-z]+){0,2})",
    r"(chef\s+de\s+projet(?:\s+(?:it|informatique|digital|technique))?)",
    r"(consultant(?:\s+(?:junior|senior|fonctionnel|technique))?(?:\s+[A-Za-z]+){0,2})",
    r"(analyste(?:\s+(?:programmeur|fonctionnel|technique|données))?)",
    r"(architecte(?:\s+(?:logiciel|solution|technique|cloud))?)",
    r"(technicien(?:\s+(?:informatique|support|réseau))?)",
    r"(responsable(?:\s+[A-Za-z]+){1,3})",
    r"(manager(?:\s+[A-Za-z]+){0,2})",
    r"(stagiaire(?:\s+[A-Za-z]+){0,3})",
    r"(alternant(?:\s+[A-Za-z]+){0,3})",
    r"(lead\s*(?:developer|tech|technique)?)",
    r"(data\s*(?:analyst|scientist|engineer)?)",
    r"(product\s*(?:owner|manager)?)",
    r"(scrum\s*master)",
]

# Entreprises connues (vraies entreprises)
KNOWN_COMPANIES = {
    "sopra steria", "capgemini", "accenture", "atos", "cgi", "thales", "orange",
    "bnp", "bnp paribas", "société générale", "societe generale", "crédit agricole",
    "axa", "allianz", "engie", "edf", "total", "airbus", "dassault", "safran",
    "sncf", "ratp", "carrefour", "auchan", "lvmh", "l'oréal", "loreal", "danone",
    "ibm", "microsoft", "google", "amazon", "meta", "apple", "oracle", "sap",
    "inetum", "netum", "alten", "altran", "astek", "sword", "devoteam", "onepoint",
    # Ajouts de services/entreprises tech
    "duolingo", "spotify", "netflix", "uber", "airbnb", "slack", "zoom", "salesforce",
    "tesla", "nvidia", "intel", "amd", "cisco", "vmware", "adobe", "autodesk"
}

def is_valid_company(name: str) -> bool:
    """Vérifie si le nom ressemble à une vraie entreprise"""
    name_lower = name.lower().strip()
    
    # Longueur minimale: une entreprise a généralement au moins 3 caractères
    if len(name_lower) < 3:
        return False
    
    # Exclure les mots simples qui ne sont pas des entreprises
    INVALID_COMPANY_WORDS = {
        # Mots génériques / adjectifs
        "bien", "mal", "détail", "détails", "négligé", "mon", "pas", "pas la", "pas le",
        "le", "la", "les", "un", "une", "de", "du", "des", "et", "ou", "à", "au", "aux",
        "je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "on", "ce", "cette",
        "que", "qui", "dont", "où", "quoi", "quel", "quelle", "full", "niveau", "pro",
        # Verbes et formes verbales
        "être", "avoir", "faire", "aller", "venir", "voir", "prendre", "donner", "mettre",
        "repasse", "respire", "travail", "travaille", "collaboration", "développement",
        # Soft skills
        "savoirs", "savoir", "savoir-être", "savoir-faire", "curiosité", "culturelle", 
        "autonomie", "calme", "sens", "méticuleux", "communication", "leadership",
        "rigueur", "organisation", "adaptabilité", "créativité", "motivation",
        # Sports / Loisirs
        "calisthénie", "sport", "musique", "lecture", "voyage", "voyages", "cinema",
        "rowing", "rowing de", "aviron",
        # Mots techniques parasites
        "serveur", "système", "jeu", "rush", "implémentation", "interaction", "implementation",
        "module", "composant", "fonction", "classe", "méthode", "variable", "objet",
        # Sections CV
        "expériences", "experience", "formations", "formation", "compétences", "competences",
        "langues", "projets", "certifications", "loisirs", "contact", "profil", "objectif",
        # Pays / Nationalités
        "pays", "france", "allemagne", "espagne", "italie", "belgique", "suisse", "français",
        "anglais", "allemand", "espagnol", "italien",
        # Mots de compétence / méthodologie (pas des entreprises)
        "agile", "scrum", "kanban", "devops", "web", "mobile", "frontend", "backend",
    }
    
    if name_lower in INVALID_COMPANY_WORDS:
        return False
    
    # Si c'est une entreprise connue
    if name_lower in KNOWN_COMPANIES:
        return True
    
    # Exclure les mots parasites
    if name_lower in STOP_ORG:
        return False
    
    # Exclure les outils/technologies
    tech_words = {"python", "java", "javascript", "html", "css", "sql", "git", "docker",
                  "react", "angular", "vue", "flask", "django", "spring", "api",
                  "plotly", "pandas", "numpy", "matplotlib", "figma", "jira", "salesforce"}
    if name_lower in tech_words:
        return False
    
    # Exclure les pays/villes
    countries_cities = {"france", "allemagne", "espagne", "italie", "belgique", "suisse",
                        "paris", "lyon", "marseille", "toulouse", "bordeaux", "nantes",
                        "boston", "londres", "berlin", "munich"}
    if name_lower in countries_cities:
        return False
    
    # Exclure les sections de CV
    sections = {"expériences", "experience", "formations", "formation", "compétences",
                "langues", "projets", "certifications", "loisirs", "contact", "profil"}
    if name_lower in sections:
        return False
    
    # Exclure les soft skills
    soft_skills = {"savoirs", "savoir", "être", "faire", "curiosité", "culturelle",
                   "autonomie", "calme", "sens", "détails", "méticuleux", "communication"}
    words_in_name = set(name_lower.split())
    if words_in_name & soft_skills:
        return False
    
    # Une entreprise valide contient généralement une majuscule
    if name.islower() and len(name.split()) == 1:
        return False
    # Un nom d'entreprise valide a généralement 1-5 mots
    if len(name.split()) > 5:
        return False
    
    return True


def detecter_sections_avec_textcat(texte: str) -> dict:
    """
    Utilise le modèle TextCat entraîné pour détecter automatiquement les sections d'un CV.
    
    PRIORITÉ: Cette fonction utilise le modèle ML entraîné (42 exemples, 10 catégories)
    au lieu de chercher des mots-clés avec des regex.
    
    Args:
        texte: Le texte complet du CV
    
    Returns:
        dict: {categorie: texte_section} pour chaque section détectée
              Catégories possibles: EDUCATION, EXPERIENCE, SKILLS, LANGUAGES, etc.
    """
    sections = {}
    
    # Diviser le texte en lignes
    lignes = texte.split('\n')
    titres_potentiels = []
    
    # Détecter les titres: lignes courtes (<50 chars), majoritairement en majuscules
    for i, ligne in enumerate(lignes):
        ligne_stripped = ligne.strip()
        if not ligne_stripped:
            continue
        
        # Un titre de section est généralement:
        # - Court (< 50 caractères)
        # - En majuscules ou commence par une majuscule
        # - Pas de ponctuation complexe
        is_short = len(ligne_stripped) < 50
        is_uppercase = sum(1 for c in ligne_stripped if c.isupper()) / max(len(ligne_stripped), 1) > 0.4
        
        if is_short and is_uppercase:
            titres_potentiels.append((i, ligne_stripped))
    
    # Pour chaque titre potentiel, extraire la section jusqu'au prochain titre
    for idx, (line_num, titre) in enumerate(titres_potentiels):
        # Trouver le prochain titre
        next_line_num = titres_potentiels[idx + 1][0] if idx + 1 < len(titres_potentiels) else len(lignes)
        
        # Extraire le texte de la section (au moins 3 lignes pour avoir du contexte)
        if next_line_num - line_num < 2:
            continue
        
        section_lines = lignes[line_num:next_line_num]
        section_text = '\n'.join(section_lines)
        
        # Classifier cette section avec TextCat
        categorie, score = classifier_section_texte(section_text, seuil_confiance=0.5)
        
        # Si la section est déjà présente, garder celle avec le meilleur score
        if categorie != "OTHER":
            if categorie not in sections or score > sections[categorie].get('score', 0):
                sections[categorie] = {
                    'texte': section_text,
                    'score': score,
                    'titre': titre
                }
    
    # Retourner seulement les textes des sections
    return {cat: info['texte'] for cat, info in sections.items()}


def extract_section_text(texte: str, section_names: List[str]) -> Optional[str]:
    """Extrait le texte d'une section spécifique du CV."""
    pattern = r'(?:' + '|'.join(section_names) + r')\s*[:\-\n]+(.+?)(?=\n\s*(?:Formations?|Expériences?|Compétences?|Langues?|Projets?|Certifications?|Loisirs?|Centres?\s+d\'intérêt)\s*[:\-\n]|$)'
    match = re.search(pattern, texte, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def parse_formation_section(texte: str) -> List[dict]:
    """
    Parse la section Formations du CV de manière structurée.
    
    PRIORITÉ: Utilise d'abord le modèle TextCat pour détecter la section EDUCATION,
    puis applique les patterns de parsing structurés.
    
    Fallback: Si TextCat ne trouve rien, utilise la recherche par mots-clés.
    """
    formations = []
    
    # === PRIORITÉ 1: Utiliser TextCat pour détecter la section EDUCATION ===
    sections_ml = detecter_sections_avec_textcat(texte)
    section_text = sections_ml.get("EDUCATION")
    
    # === FALLBACK: Recherche par mots-clés si TextCat n'a rien trouvé ===
    if not section_text:
        formation_keywords = ["FORMATION", "FORMATIONS", "ÉTUDES", "ETUDES", "ÉDUCATION", "EDUCATION", "CURSUS", "PARCOURS ACADÉMIQUE", "PARCOURS SCOLAIRE"]
        section_text = extract_section_text(texte, formation_keywords)
    
    if not section_text:
        return formations
    
    # Diviser par lignes
    lines = section_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # Ignorer les titres de section
        if re.match(r'^(formations?|études|education|cursus)\s*[:.]?$', line, re.IGNORECASE):
            continue
        
        # Ignorer les lignes qui commencent par un tiret (descriptions)
        if line.startswith('-') or line.startswith('•'):
            continue
        
        # Pattern 1: "2018-2020: Master Informatique - Université Paris"
        match1 = re.match(r'^((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|[Pp]résent|[Aa]ctuel)\s*[:\-–—]\s*(.+)$', line)
        
        # Pattern 2: "Université Paris - Master Informatique (2018-2020)"
        match2 = re.search(r'^(.+?)\s*\(((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|[Pp]résent|[Aa]ctuel)\)$', line)
        
        # Pattern 3: "École : Diplôme (Lieu)" - format du CV Léo WEBER
        match3 = re.match(r'^([A-ZÀ-Üa-zà-ÿ][A-Za-zÀ-ÿ\s\-]+?)\s*:\s*(.+?)(?:\s*\(([A-Za-zÀ-ÿ\s\-]+)\))?$', line)
        
        # Pattern 4: "Master Informatique, Université Paris, 2018-2020"
        match4 = re.match(r'^(.+?),\s*(.+?),?\s*((?:19|20)\d{2})\s*[-–—]?\s*((?:19|20)\d{2})?$', line)
        
        if match1:
            dates = f"{match1.group(1)} – {match1.group(2)}"
            rest = match1.group(3).strip()
            diplome, ecole = extract_diploma_school(rest)
            
            formations.append({
                "etablissement": ecole,
                "diplome": diplome,
                "dates": dates
            })
            
        elif match2:
            rest = match2.group(1).strip()
            dates = f"{match2.group(2)} – {match2.group(3)}"
            diplome, ecole = extract_diploma_school(rest)
            
            formations.append({
                "etablissement": ecole,
                "diplome": diplome,
                "dates": dates
            })
            
        elif match3:
            # Format "École : Description (Lieu)"
            ecole = match3.group(1).strip()
            description = match3.group(2).strip()
            lieu = match3.group(3).strip() if match3.group(3) else None
            
            # Vérifier si c'est bien une école
            if is_school_keyword(ecole) or (len(ecole) > 3 and ecole[0].isupper()):
                # Chercher un diplôme dans la description
                diplome = None
                diplome_patterns = [
                    r'(Baccalauréat\s*[A-Za-z]*(?:\s+mention\s+[A-Za-zà-ÿ\s]+)?)',
                    r'((?:Dernière\s+)?année\s+du?\s+cycle\s+ingénieur)',
                    r'(Master\s+[A-Za-zà-ÿ\s]+)',
                    r'(Licence\s+[A-Za-zà-ÿ\s]+)',
                    r'(DUT|BTS|Diplôme\s+[A-Za-zà-ÿ\s]+)'
                ]
                for pattern in diplome_patterns:
                    m = re.search(pattern, description, re.IGNORECASE)
                    if m:
                        diplome = m.group(1).strip()
                        break
                
                if not diplome:
                    diplome = description
                
                formations.append({
                    "etablissement": ecole,
                    "diplome": diplome,
                    "dates": None
                })
            
        elif match4:
            part1 = match4.group(1).strip()
            part2 = match4.group(2).strip()
            year1 = match4.group(3)
            year2 = match4.group(4) if match4.group(4) else ""
            dates = f"{year1} – {year2}" if year2 else year1
            
            if is_diploma_keyword(part1):
                diplome = part1
                ecole = part2
            else:
                diplome = part2
                ecole = part1
            
            formations.append({
                "etablissement": ecole,
                "diplome": diplome,
                "dates": dates
            })
        else:
            # Essayer de parser sans pattern strict
            date_match = re.search(r'((?:19|20)\d{2})\s*[-–—]?\s*((?:19|20)\d{2})?', line)
            if date_match:
                dates = date_match.group(0)
                rest = re.sub(r'((?:19|20)\d{2})\s*[-–—]?\s*((?:19|20)\d{2})?', '', line).strip(" -–—:,()")
                if rest:
                    diplome, ecole = extract_diploma_school(rest)
                    if ecole or diplome:
                        formations.append({
                            "etablissement": ecole,
                            "diplome": diplome,
                            "dates": dates
                        })
    
    return formations


def is_diploma_keyword(text: str) -> bool:
    """Vérifie si le texte contient un mot-clé de diplôme."""
    diploma_keywords = [
        "master", "licence", "bachelor", "doctorat", "phd", "mba", 
        "ingénieur", "ingenieur", "bts", "dut", "bac", "baccalauréat",
        "diplôme", "diplome", "certificat", "formation"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in diploma_keywords)


def is_school_keyword(text: str) -> bool:
    """Vérifie si le texte contient un mot-clé d'établissement."""
    school_keywords = [
        "université", "universite", "école", "ecole", "lycée", "lycee",
        "iut", "imt", "insa", "epita", "epitech", "hec", "essec",
        "polytechnique", "centrale", "mines", "ens", "supérieur", 
        "institut", "college", "academy", "campus"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in school_keywords)


def extract_diploma_school(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrait le diplôme et l'école d'un texte."""
    # Séparer par tiret ou virgule
    parts = re.split(r'\s*[-–—,]\s*', text)
    
    diplome = None
    ecole = None
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        if is_diploma_keyword(part) and not diplome:
            diplome = part
        elif is_school_keyword(part) and not ecole:
            ecole = part
        elif not diplome and not ecole:
            # Premier élément, deviner basé sur les majuscules
            if re.match(r'^[A-Z][a-z]', part):
                ecole = part
            else:
                diplome = part
        elif not diplome:
            diplome = part
        elif not ecole:
            ecole = part
    
    return diplome, ecole


def parse_experience_section_v2(texte: str) -> List[dict]:
    """
    Parse la section Expériences du CV de manière structurée (version améliorée).
    
    PRIORITÉ: Utilise d'abord le modèle TextCat pour détecter la section EXPERIENCE,
    puis applique les patterns de parsing structurés.
    
    Fallback: Si TextCat ne trouve rien, utilise la recherche par mots-clés.
    """
    experiences = []
    
    # === PRIORITÉ 1: Utiliser TextCat pour détecter la section EXPERIENCE ===
    sections_ml = detecter_sections_avec_textcat(texte)
    section_text = sections_ml.get("EXPERIENCE")
    
    # === FALLBACK: Recherche par mots-clés si TextCat n'a rien trouvé ===
    if not section_text:
        exp_keywords = ["EXPÉRIENCE", "EXPERIENCE", "EXPÉRIENCES", "EXPERIENCES", 
                        "EXPÉRIENCE PROFESSIONNELLE", "EXPÉRIENCES PROFESSIONNELLES",
                        "PARCOURS PROFESSIONNEL", "PROFESSIONAL EXPERIENCE"]
        section_text = extract_section_text(texte, exp_keywords)
    
    if not section_text:
        return experiences
    
    lines = section_text.split('\n')
    current_exp = None
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # Ignorer les titres de section
        if re.match(r'^(expériences?|experiences?|parcours)\s*(professionnell?e?s?)?\s*[:.]?$', line, re.IGNORECASE):
            continue
        
        # Ignorer les lignes "Projets" qui ne sont pas des expériences
        if re.search(r'projets?\s*:?\s*$', line, re.IGNORECASE):
            continue
        
        # Pattern spécial: "S3 2024 – 2025 NomEntreprise/Institution, Lieu" (format Léo WEBER)
        match_sx_full = re.match(r'^(S\d\s+(?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2})\s+(.+?)(?:,\s*(\w+))?\s*$', line)
        
        # Pattern 1: "2021-Présent: Lead DevOps chez AWS"
        match1 = re.match(r'^((?:S\d\s+)?(?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|[Pp]résent|[Aa]ctuel(?:lement)?)\s*[:\-–—,]\s*(.+)$', line)
        
        # Pattern 2: "Lead DevOps - AWS (2021-Présent)"
        match2 = re.search(r'^(.+?)\s*\(((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|[Pp]résent|[Aa]ctuel)\)$', line)
        
        # Pattern 3: "S2 2023 Paris" (date + lieu, sans entreprise explicite)
        match3 = re.match(r'^(S\d\s+(?:19|20)\d{2})\s+([A-ZÀ-Ü][A-Za-zÀ-ÿ\s\-]+)$', line)
        
        # Pattern 4: "Stage de X semaines chez ENTREPRISE en tant que POSTE"
        match4 = re.search(r'[Ss]tage\s+(?:de\s+\d+\s+\w+\s+)?chez\s+([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-]+?)\s+en\s+tant\s+que\s+(.+)', line, re.IGNORECASE)
        
        # Pattern "Poste chez Entreprise"
        match_chez = re.search(r'^(.+?)\s+(?:chez|à|at|@)\s+([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-\']+)', line, re.IGNORECASE)
        
        if match4:
            # "Stage chez X en tant que Y"
            if current_exp and current_exp.get("entreprise"):
                experiences.append(current_exp)
            
            entreprise = match4.group(1).strip()
            poste = match4.group(2).strip()
            
            # Récupérer la date de l'expérience courante s'il y en a une
            dates = current_exp.get("dates") if current_exp else None
            
            current_exp = {
                "entreprise": entreprise,
                "poste": poste.title(),
                "dates": dates,
                "description": None
            }
            
        elif match_sx_full:
            # Format "S3 2024 – 2025 Rhine-Waal University, Allemagne"
            if current_exp and current_exp.get("entreprise"):
                experiences.append(current_exp)
            
            dates = f"{match_sx_full.group(1)} – {match_sx_full.group(2)}"
            institution = match_sx_full.group(3).strip()
            lieu = match_sx_full.group(4).strip() if match_sx_full.group(4) else None
            
            # Nettoyer l'institution (enlever les tirets parasites)
            institution = re.sub(r'\s*[-–—]\s*', '-', institution).strip('-').strip()
            
            current_exp = {
                "entreprise": institution,
                "poste": "Échange universitaire" if is_school_keyword(institution) else None,
                "dates": dates,
                "lieu": lieu,
                "description": None
            }
            
        elif match1:
            if current_exp and current_exp.get("entreprise"):
                experiences.append(current_exp)
            
            dates = f"{match1.group(1)} – {match1.group(2)}"
            rest = match1.group(3).strip()
            
            poste, entreprise, lieu = extract_job_company(rest)
            
            # Si pas d'entreprise mais un lieu détecté, c'est peut-être le nom
            if not entreprise and lieu:
                entreprise = lieu
                lieu = None
            
            current_exp = {
                "entreprise": entreprise,
                "poste": poste,
                "dates": dates,
                "description": None
            }
            
        elif match3:
            # Format "S2 2023 Paris" - stocker la date/lieu pour le prochain
            if current_exp and current_exp.get("entreprise"):
                experiences.append(current_exp)
            
            dates = match3.group(1)
            lieu = match3.group(2).strip()
            
            current_exp = {
                "entreprise": None,
                "poste": None,
                "dates": dates,
                "lieu": lieu,
                "description": None
            }
            
        elif match2:
            if current_exp and current_exp.get("entreprise"):
                experiences.append(current_exp)
            
            rest = match2.group(1).strip()
            dates = f"{match2.group(2)} – {match2.group(3)}"
            
            poste, entreprise, lieu = extract_job_company(rest)
            
            current_exp = {
                "entreprise": entreprise,
                "poste": poste,
                "dates": dates,
                "description": None
            }
            
        elif match_chez:
            if current_exp and current_exp.get("entreprise"):
                experiences.append(current_exp)
            
            poste = match_chez.group(1).strip()
            entreprise = match_chez.group(2).strip()
            
            # Chercher la date
            date_match = re.search(r'((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|[Pp]résent|[Aa]ctuel)', line)
            dates = date_match.group(0) if date_match else None
            
            # Si l'expérience courante a une date mais pas d'entreprise, l'utiliser
            if not dates and current_exp and current_exp.get("dates"):
                dates = current_exp.get("dates")
            
            current_exp = {
                "entreprise": entreprise,
                "poste": poste.title() if poste else None,
                "dates": dates,
                "description": None
            }
            
        elif current_exp and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
            # Ligne de description
            desc_line = line.lstrip('-•*').strip()
            
            # Chercher si c'est une description qui contient "chez ENTREPRISE en tant que POSTE"
            chez_in_desc = re.search(r'[Ss]tage\s+(?:de\s+\d+\s+\w+\s+)?chez\s+([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-]+?)\s+en\s+tant\s+que\s+(.+)', desc_line, re.IGNORECASE)
            if chez_in_desc and not current_exp.get("entreprise"):
                current_exp["entreprise"] = chez_in_desc.group(1).strip()
                current_exp["poste"] = chez_in_desc.group(2).strip().title()
            
            if current_exp.get("description"):
                current_exp["description"] += "\n- " + desc_line
            else:
                current_exp["description"] = "- " + desc_line
    
    # Ajouter la dernière expérience
    if current_exp and current_exp.get("entreprise"):
        experiences.append(current_exp)
    
    return experiences


def extract_job_company(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extrait le poste, l'entreprise et le lieu d'un texte."""
    poste = None
    entreprise = None
    lieu = None
    
    # Pattern "chez/à/at ENTREPRISE"
    chez_match = re.search(r'\s+(?:chez|à|at|@)\s+([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-\']+)', text, re.IGNORECASE)
    if chez_match:
        entreprise = chez_match.group(1).strip()
        poste_text = text[:chez_match.start()].strip()
        after = text[chez_match.end():].strip(" -–—:,")
        
        # Chercher un poste connu dans le texte avant
        for pattern in POSTE_PATTERNS:
            m = re.search(pattern, poste_text, re.IGNORECASE)
            if m:
                poste = m.group(1).strip().title()
                break
        
        if not poste and poste_text:
            poste = poste_text.title()
        
        # Le texte après pourrait être le lieu
        if after and len(after) > 2 and len(after) < 30:
            lieu = after
    else:
        # Séparer par tiret ou virgule
        parts = re.split(r'\s*[-–—]\s*', text)
        
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            
            # Chercher un poste connu
            is_poste = False
            for pattern in POSTE_PATTERNS:
                if re.search(pattern, part, re.IGNORECASE):
                    poste = part.title()
                    is_poste = True
                    break
            
            if not is_poste:
                if is_valid_company(part) and not entreprise:
                    entreprise = part
                elif not lieu and len(part) < 30:
                    lieu = part
    
    return poste, entreprise, lieu


def parse_experience_section(texte: str) -> List[dict]:
    """
    Parse la section Expériences du CV de manière structurée.
    Cherche le pattern: Date - Entreprise - Poste - Description
    """
    experiences = []
    
    # Pattern pour détecter le début d'une expérience
    # Format: "S2 2023 Paris" ou "2022 - 2023" ou "Janvier 2022 - Présent"
    exp_pattern = re.compile(
        r'(?:S\d\s+)?'  # Optionnel: Semestre
        r'((?:19|20)\d{2})'  # Année début
        r'(?:\s*[-–—]\s*(?:((?:19|20)\d{2})|[Pp]résent|[Aa]ctuel))?'  # Optionnel: Année fin
        r'[,\s]*'
        r'([A-ZÀ-Ü][A-Za-zÀ-ÿ\s\-\']+)?'  # Lieu ou entreprise
    )
    
    # Chercher la section Expériences
    exp_section_match = re.search(
        r'(?:Expériences?\s*(?:professionnelles?)?|Professional\s+Experience)\s*[:\-\n]+(.+?)(?=\n\s*(?:Formations?|Compétences?|Langues?|Certifications?|Projets?|Loisirs?)\s*[:\-\n]|$)',
        texte, 
        re.IGNORECASE | re.DOTALL
    )
    
    if exp_section_match:
        exp_text = exp_section_match.group(1)
        
        # Diviser par lignes et chercher les entrées
        lines = exp_text.split('\n')
        current_exp = None
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Chercher une date de début d'expérience
            date_match = re.search(r'((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|[Pp]résent|[Aa]ctuel)', line)
            
            if date_match:
                # Nouvelle expérience détectée
                if current_exp and current_exp.get("entreprise"):
                    experiences.append(current_exp)
                
                dates = f"{date_match.group(1)} – {date_match.group(2)}"
                
                # Chercher l'entreprise et le poste dans la ligne
                rest = line[date_match.end():].strip(" -–—:,")
                
                # Chercher "chez ENTREPRISE" ou "à ENTREPRISE"
                chez_match = re.search(r'(?:chez|à|at|@)\s+([A-ZÀ-Ü][A-Za-zÀ-ÿ\s\-\']+)', rest, re.IGNORECASE)
                
                entreprise = None
                poste = None
                
                if chez_match:
                    entreprise = chez_match.group(1).strip()
                    poste = rest[:chez_match.start()].strip(" -–—:,")
                else:
                    # Chercher un poste connu
                    for pattern in POSTE_PATTERNS:
                        m = re.search(pattern, rest, re.IGNORECASE)
                        if m:
                            poste = m.group(1).strip().title()
                            # L'entreprise est peut-être avant ou après le poste
                            before = rest[:m.start()].strip(" -–—:,")
                            after = rest[m.end():].strip(" -–—:,")
                            if before and len(before) > 2:
                                entreprise = before
                            elif after and len(after) > 2:
                                entreprise = after
                            break
                
                current_exp = {
                    "entreprise": entreprise,
                    "poste": poste,
                    "dates": dates,
                    "description": ""
                }
            
            elif current_exp:
                # Ligne de description
                if line.startswith('-') or line.startswith('•'):
                    desc_line = line.lstrip('-•').strip()
                    if current_exp["description"]:
                        current_exp["description"] += "\n- " + desc_line
                    else:
                        current_exp["description"] = "- " + desc_line
        
        # Ajouter la dernière expérience
        if current_exp and current_exp.get("entreprise"):
            experiences.append(current_exp)
    
    return experiences

def extract_poste_from_context(context: str) -> Optional[str]:
    """Extrait le poste/titre du contexte avec des patterns améliorés"""
    for pattern in POSTE_PATTERNS:
        m = re.search(pattern, context, re.IGNORECASE)
        if m:
            poste = m.group(1).strip()
            poste = re.sub(r'\s+', ' ', poste)
            return poste.title()
    return None

def extract_titre_profil(texte: str) -> Optional[str]:
    """Extrait le titre/profil du candidat (ex: Développeur Full Stack)"""
    lines = [l.strip() for l in texte.split('\n') if l.strip()][:20]
    
    for line in lines:
        if len(line) < 5 or len(line) > 80:
            continue
        if re.search(r'[@\d]{6,}', line):
            continue
        
        for pattern in POSTE_PATTERNS:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                return m.group(1).strip().title()
    
    return None

def classifier_formations_experiences(texte: str, entites: dict, dates: List[str]):
    formations, experiences = [], []
    date_spans = extract_date_spans(texte)

    # === PRIORITÉ 1: Utiliser les entités du modèle NER entraîné ===
    # Le modèle a été entraîné sur 322 exemples, il faut lui faire confiance !
    
    # 1. Formations depuis les écoles détectées par le modèle entraîné
    for ecole in entites.get("ecoles", []):
        ecole_clean = nettoyer_nom_organisation(ecole)
        if not ecole_clean or ecole_clean.lower() in STOP_ORG:
            continue
        # Valider que c'est un vrai établissement
        if not is_valid_school(ecole_clean):
            continue
        
        date_assoc = find_closest_date_by_char(ecole_clean, texte, date_spans)
        
        # Chercher le diplôme associé
        diplome = None
        for dip in entites.get("diplomes", []):
            # Vérifier si le diplôme est proche de l'école dans le texte
            idx_ecole = texte.lower().find(ecole_clean.lower())
            idx_dip = texte.lower().find(dip.lower())
            if idx_ecole != -1 and idx_dip != -1:
                if abs(idx_ecole - idx_dip) < 200:  # Proximité de 200 caractères
                    diplome = dip
                    break
        
        formations.append({
            "etablissement": ecole_clean,
            "dates": date_assoc,
            "diplome": diplome
        })
    
    # 2. Expériences depuis les entreprises détectées par le modèle entraîné
    ecoles_lower = {e.lower() for e in entites.get("ecoles", [])}
    for entreprise in entites.get("organisations", []):
        entreprise_clean = nettoyer_nom_organisation(entreprise)
        if not entreprise_clean or entreprise_clean.lower() in STOP_ORG:
            continue
        # Éviter les doublons avec les écoles
        if entreprise_clean.lower() in ecoles_lower:
            continue
        if not is_valid_company(entreprise_clean):
            continue
        
        date_assoc = find_closest_date_by_char(entreprise_clean, texte, date_spans)
        
        # Chercher le poste associé
        poste = None
        for p in entites.get("postes", []):
            idx_ent = texte.lower().find(entreprise_clean.lower())
            idx_poste = texte.lower().find(p.lower())
            if idx_ent != -1 and idx_poste != -1:
                if abs(idx_ent - idx_poste) < 200:
                    poste = p.title()
                    break
        
        if not poste:
            sentences = re.split(r'[.!\n]', texte)
            for s in sentences:
                if entreprise_clean.lower() in s.lower():
                    poste = extract_poste_from_context(s)
                    break
        
        if not poste:
            idx = texte.lower().find(entreprise_clean.lower())
            if idx != -1:
                window = texte[max(0, idx-100):min(len(texte), idx+150)]
                poste = extract_poste_from_context(window)
        
        experiences.append({
            "entreprise": entreprise_clean,
            "poste": poste,
            "dates": date_assoc,
            "description": None
        })
    
    # === FALLBACK: Si NER n'a rien trouvé, utiliser les parsers heuristiques ===
    if not formations:
        parsed_formations = parse_formation_section(texte)
        if parsed_formations:
            for f in parsed_formations:
                if f.get("etablissement") or f.get("diplome"):
                    # Valider l'établissement si présent
                    if f.get("etablissement") and not is_valid_school(f["etablissement"]):
                        continue
                    formations.append({
                        "etablissement": f.get("etablissement"),
                        "dates": f.get("dates"),
                        "diplome": f.get("diplome")
                    })
    
    if not experiences:
        parsed_experiences = parse_experience_section_v2(texte)
        if parsed_experiences:
            for e in parsed_experiences:
                if e.get("entreprise") and is_valid_company(e["entreprise"]):
                    experiences.append(e)

    # === ENRICHISSEMENT: Ajouter les organisations non classifiées par le NER ===
    formations_lower = {f["etablissement"].lower() for f in formations if f.get("etablissement")}
    experiences_lower = {e["entreprise"].lower() for e in experiences if e.get("entreprise")}
    
    for org in entites.get("organisations", []):
        org_clean = nettoyer_nom_organisation(org)
        if not org_clean or org_clean.lower() in STOP_ORG:
            continue
        if org_clean.lower() in EXPERIENCE_KEYWORDS:
            continue
        if len(org_clean) < 2:
            continue
        
        # Éviter les doublons
        if org_clean.lower() in formations_lower or org_clean.lower() in experiences_lower:
            continue
        
        # Valider que c'est une vraie entreprise/établissement
        if not is_valid_company(org_clean) and not is_formation(org_clean, ""):
            continue

        date_assoc = find_closest_date_by_char(org_clean, texte, date_spans)
        
        sentences = re.split(r'[.!\n]', texte)
        context = ""
        for s in sentences:
            if org_clean.lower() in s.lower():
                context = s
                break
        
        poste = extract_poste_from_context(context)
        
        if not poste:
            idx = texte.lower().find(org_clean.lower())
            if idx != -1:
                window = texte[max(0, idx-100):min(len(texte), idx+150)]
                poste = extract_poste_from_context(window)

        if is_formation(org_clean, context):
            diplome_match = re.search(r"(Master|Licence|Bachelor|DUT|BTS|Ingénieur|Doctorat|MBA)(?:\s+[A-Za-zÀ-ÿ]+){0,4}", context, re.IGNORECASE)
            diplome = diplome_match.group(0).strip() if diplome_match else None
            formations.append({
                "etablissement": org_clean, 
                "dates": date_assoc,
                "diplome": diplome
            })
        else:
            if not is_valid_company(org_clean):
                continue
                
            description = ""
            if context:
                desc_match = re.search(rf"{re.escape(org_clean)}[^.]*\.([^.]+\.)", texte, re.IGNORECASE)
                if desc_match:
                    description = desc_match.group(1).strip()
            
            experiences.append({
                "entreprise": org_clean, 
                "poste": poste, 
                "dates": date_assoc,
                "description": description if description else None
            })

    for item in formations + experiences:
        if item.get("dates") in (None, "", "2025-11-12", "2026-01-03"):
            match = re.search(r"(?:19|20)\d{2}\s*[-–—]\s*(?:(?:19|20)\d{2}|[Pp]résent|[Aa]ctuel)", texte)
            if match:
                item["dates"] = match.group(0)

    dedupe = lambda l, k: list({d[k]: d for d in l if d.get(k)}.values())
    return dedupe(formations, "etablissement"), dedupe(experiences, "entreprise")


# ---------------------
# 5️ Construction JSON + affichage rich
# ---------------------
def build_structured_json(emails, telephones, adresses, dates, texte_cv):
    entites = extraire_entites(texte_cv)
    entites["organisations"] = nettoyer_organisations(entites.get("organisations", []))

    # === Nom (PRIORITÉ : extraction depuis l'en-tête) ===
    nom = extract_name_from_header(texte_cv)
    
    # Fallback: utiliser spaCy si l'heuristique échoue
    if not nom and entites.get("noms"):
        for candidate in entites["noms"]:
            candidate_clean = candidate.strip()
            words = candidate_clean.lower().split()
            # Vérifier que le nom n'est pas un mot parasite
            if not any(w in NAME_EXCLUSIONS for w in words):
                nom = candidate_clean
                break
    
    # Nettoyage final du nom
    if nom:
        nom = re.sub(
            r"\b(?:développeur|developer|ingénieur|consultant|manager|full\s*stack|data|web|chef|stagiaire|alternant)\b.*",
            "",
            nom,
            flags=re.IGNORECASE
        ).strip()
        nom = re.sub(r"[\-–—:,]+$", "", nom).strip()
        
        # Dernière vérification: le nom ne doit pas être un mot parasite
        if nom.lower() in NAME_EXCLUSIONS or any(w in nom.lower() for w in ["savoirs", "être", "soft", "hard", "skills"]):
            nom = None

    # === Titre du profil ===
    titre_profil = extract_titre_profil(texte_cv)
    
    if not titre_profil:
        for pattern in POSTE_PATTERNS[:5]:
            m = re.search(pattern, texte_cv[:500], re.IGNORECASE)
            if m:
                titre_profil = m.group(1).strip().title()
                break

    # === Contact ===
    contact = {
        "nom": nom,
        "email": emails[0] if emails else None,
        "telephone": telephones[0] if telephones else None,
        "adresse": adresses[0] if adresses else None,
    }

    # === Sections ===
    formations, experiences = classifier_formations_experiences(texte_cv, entites, dates)
    
    # FALLBACK: Si pas d'expériences valides, utiliser le parser de section
    if not experiences or len(experiences) < 1:
        parsed_exp = parse_experience_section(texte_cv)
        if parsed_exp:
            experiences = parsed_exp
    
    # Filtrer les expériences invalides (fausses entreprises)
    valid_experiences = []
    for exp in experiences:
        entreprise = exp.get("entreprise", "")
        if entreprise and is_valid_company(entreprise):
            valid_experiences.append(exp)
        elif entreprise and entreprise.lower() in KNOWN_COMPANIES:
            valid_experiences.append(exp)
    experiences = valid_experiences if valid_experiences else experiences
    
    comp_kw, lang_kw = extraire_competences_langues(texte_cv)
    comp_sec = parse_section_competences(texte_cv)
    lang_sec = parse_section_langues(texte_cv)
    projets = parse_section_projets(texte_cv)
    certifs = parse_section_certifications(texte_cv)
    loisirs = parse_section_loisirs(texte_cv)
    dispo = parse_disponibilite(texte_cv)

    # === Nettoyage des listes avec meilleure normalisation ===
    # Mots à exclure des compétences
    COMPETENCE_EXCLUSIONS = {
        "savoirs", "savoir", "être", "faire", "soft", "hard", "skills",
        "outils", "informatique", "microsoft", "langage", "langages",
        "css.", "html.", "et", "ou", "le", "la", "les", "de", "du", "des",
        "principales", "principale", "autres", "autre", "divers",
        "autonomie", "curiosité culturelle", "sens du détails", "méticuleux"
    }
    
    def clean_list(values, preserve_case=False):
        out = []
        seen = set()
        for x in values:
            if not x or not isinstance(x, str):
                continue
            x = x.strip()
            x_norm = x.lower()
            
            # Exclure les mots parasites
            if x_norm in COMPETENCE_EXCLUSIONS:
                continue
            # Exclure si trop court ou trop long
            if len(x) < 2 or len(x) > 50:
                continue
            # Exclure les compétences qui sont juste des préfixes
            if x_norm.endswith(':') or x_norm.startswith(':'):
                continue
            # Exclure les codes postaux (5 chiffres)
            if re.match(r'^\d{5}$', x):
                continue
            # Exclure les numéros purs
            if x.isdigit():
                continue
                
            if x_norm and x_norm not in seen:
                seen.add(x_norm)
                if preserve_case:
                    out.append(x)
                else:
                    out.append(x.capitalize() if not x.isupper() else x)
        return out

    competences = clean_list(
        entites.get("competences", []) +
        comp_kw +
        comp_sec,
        preserve_case=True
    )
    
    # Nettoyer les compétences mal formées
    competences_clean = []
    for comp in competences:
        # Supprimer les préfixes comme "Langage informatiques :"
        comp = re.sub(r'^(?:Langage|Outils?|Analyse|Gestion)[^\:]*:\s*', '', comp, flags=re.IGNORECASE)
        comp = comp.strip()
        if comp and len(comp) >= 2 and comp.lower() not in COMPETENCE_EXCLUSIONS:
            competences_clean.append(comp)
    competences = competences_clean

    langues = clean_list(
        entites.get("langues", []) +
        lang_kw +
        lang_sec
    )

    # === Construction du JSON final avec validation ===
    json_final = {
        "contact": contact,
        "titre_profil": titre_profil,
        "formations": formations if formations else [],
        "experiences": experiences if experiences else [],
        "competences": sorted(set(competences)) if competences else [],
        "langues": sorted(set(langues)) if langues else [],
        "projets": projets if projets else [],
        "certifications": certifs if certifs else [],
        "loisirs": loisirs if loisirs else [],
        "disponibilite": dispo,
        "dates": dates if dates else [],
    }

    # === Sauvegarde dans /data/output ===
    def save_to_output_folder(json_data):
        output_dir = "data/output"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"cv_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(output_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

        print(f"\n📁 Résultat JSON enregistré ici : {path}\n")

    save_to_output_folder(json_final)

    # === Affichage console ===
    table = Table(title="Résultats d'analyse du CV", show_header=True, header_style="bold magenta")
    table.add_column("Section", style="cyan", no_wrap=True)
    table.add_column("Contenu principal", style="white")
    table.add_row("👤 Nom", nom or "—")
    table.add_row("📧 Email", contact["email"] or "—")
    table.add_row("📞 Téléphone", contact["telephone"] or "—")
    table.add_row("🏠 Adresse", contact["adresse"] or "—")
    table.add_row("🎓 Formations", str([f"{f['etablissement']} ({f['dates']})" for f in formations]))
    table.add_row("💼 Expériences", str([f"{e['entreprise']} - {e.get('poste', '—')} ({e['dates']})" for e in experiences]))
    table.add_row("🧠 Compétences", ", ".join(competences[:10]))
    table.add_row("🌐 Langues", ", ".join(langues))
    table.add_row("🚀 Projets", ", ".join(projets) or "—")
    table.add_row("🏅 Certifications", ", ".join(certifs) or "—")
    table.add_row("🎯 Loisirs", ", ".join(loisirs) or "—")
    table.add_row("📅 Disponibilité", dispo or "—")
    console.print(table)

    return json_final
