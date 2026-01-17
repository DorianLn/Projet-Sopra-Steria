# backend/extractors/heuristic_rules.py
"""
Règles heuristiques renforcées pour l'extraction structurée de CV.

Ce module contient les patterns et règles pour :
- Structuration temporelle (dates, périodes)
- Structuration sémantique (postes, diplômes, entreprises, écoles)
- Validation et normalisation des entités extraites

Ces règles complètent le NER spaCy pour améliorer la précision d'extraction.
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# =============================================================================
# PATTERNS DE DATES
# =============================================================================

DATE_PATTERNS = {
    # Plages de dates
    "range_year": r"(?P<start>(?:19|20)\d{2})\s*[-–—]\s*(?P<end>(?:19|20)\d{2}|[Pp]résent|[Aa]ctuel(?:lement)?|[Aa]ujourd'?hui)",
    "range_month_year": r"(?P<start_m>\w+)\s+(?P<start_y>\d{4})\s*[-–—]\s*(?P<end_m>\w+)?\s*(?P<end_y>\d{4}|[Pp]résent|[Aa]ctuel)",
    
    # Semestres (format EPITA/école)
    "semester": r"[Ss](?P<sem>\d)\s+(?P<year>(?:19|20)\d{2})",
    "semester_range": r"[Ss](?P<sem>\d)\s+(?P<start>(?:19|20)\d{2})\s*[-–—]\s*(?P<end>(?:19|20)\d{2})",
    
    # Années simples
    "year_single": r"\b(?P<year>(?:19|20)\d{2})\b",
    
    # Format mois/année
    "month_year": r"(?P<month>(?:Janvier|Février|Fevrier|Mars|Avril|Mai|Juin|Juillet|Août|Aout|Septembre|Octobre|Novembre|Décembre))\s+(?P<year>\d{4})",
    
    # Durées
    "duration": r"(?P<num>\d+)\s*(?P<unit>ans?|mois|semaines?|jours?)",
    
    # "depuis X"
    "since": r"[Dd]epuis\s+(?:(?P<month>\w+)\s+)?(?P<year>(?:19|20)\d{2})",
}

MONTHS_FR = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
}

# =============================================================================
# PATTERNS DE POSTES
# =============================================================================

JOB_TITLE_PATTERNS = [
    # Développeur/Ingénieur + spécialité
    r"(?P<title>(?:Développeur|Developpeur|Ingénieur|Ingenieur|Engineer)\s+(?:Full\s*Stack|Frontend|Backend|Web|Mobile|DevOps|Cloud|Data|Python|Java|\.NET|C\+\+|React|Angular|Vue\.?js?))",
    
    # Titres composés
    r"(?P<title>(?:Lead|Senior|Junior|Stagiaire|Alternant)\s+(?:Développeur|Developpeur|Ingénieur|Ingenieur|Data\s*Scientist|DevOps|Analyst))",
    
    # Postes management
    r"(?P<title>Chef\s+de\s+[Pp]rojet(?:\s+(?:Digital|IT|Web|Technique))?)",
    r"(?P<title>(?:Scrum|Product|Project)\s*(?:Master|Owner|Manager))",
    
    # Consultants
    r"(?P<title>Consultant(?:\s+(?:IT|Tech|Digital|Senior|Junior|Fonctionnel|Technique))?)",
    
    # Analystes
    r"(?P<title>(?:Business|Data|Functional)\s*Analyst(?:\s+(?:Senior|Junior))?)",
    
    # Architectes
    r"(?P<title>Architect(?:e)?\s+(?:Solution|Cloud|Logiciel|Software|Technique))",
    
    # Stages/Alternances
    r"(?P<title>Stage(?:iaire)?\s+(?:Développeur|Developpeur|Ingénieur|Data|DevOps|Web)(?:\s+\w+)?)",
    r"(?P<title>Alternance?\s+(?:Développeur|Developpeur|Ingénieur|Data)(?:\s+\w+)?)",
]

# Mots-clés de postes
JOB_KEYWORDS = {
    "senior_titles": ["lead", "senior", "principal", "staff", "chief", "head", "director", "manager"],
    "junior_titles": ["junior", "stagiaire", "alternant", "intern", "trainee", "apprenti"],
    "tech_roles": ["développeur", "developpeur", "ingénieur", "ingenieur", "engineer", "developer", 
                   "architecte", "architect", "devops", "sre", "data scientist", "data engineer",
                   "ml engineer", "fullstack", "full stack", "frontend", "backend"],
    "management_roles": ["manager", "chef de projet", "project manager", "scrum master", 
                        "product owner", "team lead", "tech lead", "cto", "cio"],
    "consulting_roles": ["consultant", "analyst", "business analyst", "functional analyst"],
}

# =============================================================================
# PATTERNS DE DIPLÔMES
# =============================================================================

DIPLOMA_PATTERNS = [
    # Masters
    r"(?P<diploma>Master(?:'s)?\s+(?:(?:of\s+)?(?:Science|Business|Arts|Engineering)?\s*)?(?:\w+(?:\s+\w+){0,3}))",
    r"(?P<diploma>M2?\s+(?:\w+(?:\s+\w+){0,2}))",
    
    # Ingénieur
    r"(?P<diploma>(?:Diplôme\s+d'?|Cycle\s+)?[Ii]ngénieur(?:\s+(?:spécialité|option)?\s*\w+(?:\s+\w+){0,2})?)",
    
    # Licences
    r"(?P<diploma>(?:Licence|License|Bachelor)(?:'s)?\s+(?:\w+(?:\s+\w+){0,2}))",
    r"(?P<diploma>L[123]\s+(?:\w+(?:\s+\w+){0,2}))",
    
    # BTS/DUT/BUT
    r"(?P<diploma>(?:BTS|DUT|BUT|IUT)\s+(?:\w+(?:\s+\w+){0,3}))",
    
    # Baccalauréat
    r"(?P<diploma>Bac(?:calauréat)?\s+(?:S|ES|L|STI2D|STMG|Pro)?(?:\s+(?:mention\s+)?(?:très\s+bien|bien|assez\s+bien|AB|B|TB))?)",
    
    # Prépa
    r"(?P<diploma>(?:Prépa|Prépas?|CPGE)\s+(?:MPSI|PCSI|MP|PC|PSI|PT|BCPST|ECE|ECS|ECG|B/L)(?:/\*)?)",
    
    # Doctorat
    r"(?P<diploma>(?:Doctorat|PhD|Ph\.?D\.?)\s+(?:en\s+)?(?:\w+(?:\s+\w+){0,3}))",
    
    # MBA
    r"(?P<diploma>MBA(?:\s+(?:\w+(?:\s+\w+){0,2}))?)",
    
    # Certifications
    r"(?P<diploma>(?:Certification|Certified)\s+(?:\w+(?:\s+\w+){0,3}))",
]

DIPLOMA_KEYWORDS = [
    "master", "licence", "bachelor", "ingénieur", "ingenieur", "doctorat", "phd",
    "mba", "bts", "dut", "but", "bac", "baccalauréat", "prépa", "cpge",
    "diplôme", "diplome", "certificat", "certification", "formation",
    "cycle", "spécialité", "specialite", "option", "mention"
]

# =============================================================================
# PATTERNS D'ÉCOLES/UNIVERSITÉS
# =============================================================================

SCHOOL_PATTERNS = [
    # Universités
    r"(?P<school>Université\s+(?:de\s+)?(?:[A-ZÀ-Ü][a-zà-ÿ]+(?:[\s\-][A-Za-zÀ-ÿ]+)*))",
    r"(?P<school>University\s+of\s+\w+(?:\s+\w+)?)",
    
    # Grandes écoles
    r"(?P<school>École\s+(?:Polytechnique|Centrale|Normale\s+Supérieure|des\s+Mines|des\s+Ponts)(?:\s+(?:de\s+)?[A-Za-zÀ-ÿ]+)?)",
    r"(?P<school>(?:HEC|ESSEC|ESCP|EM\s*Lyon|EDHEC|Audencia)(?:\s+[A-Za-zÀ-ÿ]+)?)",
    
    # Écoles d'ingénieurs
    r"(?P<school>(?:EPITA|EPITECH|INSA|ENSEEIHT|ENSIMAG|Centrale|Mines|Telecom|IMT|ISEP|ECE|EFREI|ESIEA|SUPINFO)(?:\s+[A-Za-zÀ-ÿ]+)?)",
    
    # IUT
    r"(?P<school>IUT\s+(?:de\s+)?[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)?)",
    
    # Lycées
    r"(?P<school>Lycée\s+(?:[A-ZÀ-Ü][a-zà-ÿ]+(?:[\s\-][A-Za-zÀ-ÿ]+)*))",
]

SCHOOL_KEYWORDS = [
    "université", "universite", "university", "école", "ecole", "school",
    "lycée", "lycee", "iut", "institut", "faculty", "faculté", "campus",
    "epita", "epitech", "insa", "hec", "essec", "polytechnique", "centrale",
    "mines", "ens", "normale supérieure", "imt", "isep", "ece", "efrei"
]

# =============================================================================
# PATTERNS D'ENTREPRISES
# =============================================================================

COMPANY_PATTERNS = [
    # Grands groupes connus
    r"\b(?P<company>(?:Sopra\s*Steria|Capgemini|Accenture|Atos|CGI|IBM|Microsoft|Google|Amazon|Meta|Apple|Oracle|SAP|Salesforce))\b",
    r"\b(?P<company>(?:Orange|SFR|Bouygues|Thales|Airbus|Safran|Dassault|Total|EDF|Engie|SNCF|BNP\s*Paribas|Société\s*Générale))\b",
    
    # Pattern générique "chez/at ENTREPRISE"
    r"(?:chez|at|@)\s+(?P<company>[A-ZÀ-Ü][A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,2})",
    
    # Pattern "ENTREPRISE - Poste"
    r"(?P<company>[A-ZÀ-Ü][A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)?)\s*[-–—]\s*(?:Ingénieur|Développeur|Consultant|Stage|Alternance)",
]

COMPANY_KEYWORDS = [
    "sopra", "steria", "capgemini", "accenture", "atos", "cgi", "ibm", "microsoft",
    "google", "amazon", "meta", "apple", "oracle", "sap", "salesforce",
    "orange", "thales", "airbus", "safran", "bnp", "société générale",
    "sncf", "edf", "engie", "total", "ubisoft", "dassault"
]

# =============================================================================
# FONCTIONS D'EXTRACTION HEURISTIQUE
# =============================================================================

def extract_dates_heuristic(text: str) -> List[Dict]:
    """
    Extrait toutes les dates et périodes avec leur contexte.
    
    Returns:
        List[Dict] avec: raw, start, end, normalized, type (range/single/semester)
    """
    results = []
    
    # Plages d'années
    for match in re.finditer(DATE_PATTERNS["range_year"], text, re.IGNORECASE):
        results.append({
            "raw": match.group(0),
            "start_pos": match.start(),
            "end_pos": match.end(),
            "start_date": match.group("start"),
            "end_date": match.group("end"),
            "type": "range"
        })
    
    # Semestres
    for match in re.finditer(DATE_PATTERNS["semester"], text, re.IGNORECASE):
        sem = match.group("sem")
        year = match.group("year")
        results.append({
            "raw": match.group(0),
            "start_pos": match.start(),
            "end_pos": match.end(),
            "semester": int(sem),
            "year": year,
            "type": "semester"
        })
    
    # Semestres avec plage
    for match in re.finditer(DATE_PATTERNS["semester_range"], text, re.IGNORECASE):
        results.append({
            "raw": match.group(0),
            "start_pos": match.start(),
            "end_pos": match.end(),
            "semester": int(match.group("sem")),
            "start_date": match.group("start"),
            "end_date": match.group("end"),
            "type": "semester_range"
        })
    
    # "depuis X"
    for match in re.finditer(DATE_PATTERNS["since"], text, re.IGNORECASE):
        results.append({
            "raw": match.group(0),
            "start_pos": match.start(),
            "end_pos": match.end(),
            "start_date": match.group("year"),
            "end_date": "Présent",
            "type": "since"
        })
    
    # Supprimer les doublons par position
    seen_positions = set()
    unique_results = []
    for r in sorted(results, key=lambda x: -len(x["raw"])):  # Préférer les matches plus longs
        if r["start_pos"] not in seen_positions:
            unique_results.append(r)
            seen_positions.add(r["start_pos"])
    
    return sorted(unique_results, key=lambda x: x["start_pos"])


def extract_job_title_heuristic(text: str) -> List[Dict]:
    """
    Extrait les postes/titres de fonction avec patterns heuristiques.
    """
    results = []
    
    for pattern in JOB_TITLE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            title = match.group("title").strip()
            # Normaliser la casse
            title = title.title()
            results.append({
                "raw": match.group(0),
                "title": title,
                "start_pos": match.start(),
                "end_pos": match.end()
            })
    
    return results


def extract_diploma_heuristic(text: str) -> List[Dict]:
    """
    Extrait les diplômes avec patterns heuristiques.
    """
    results = []
    
    for pattern in DIPLOMA_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            diploma = match.group("diploma").strip()
            results.append({
                "raw": match.group(0),
                "diploma": diploma,
                "start_pos": match.start(),
                "end_pos": match.end()
            })
    
    return results


def extract_school_heuristic(text: str) -> List[Dict]:
    """
    Extrait les écoles/universités avec patterns heuristiques.
    """
    results = []
    
    for pattern in SCHOOL_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            school = match.group("school").strip()
            results.append({
                "raw": match.group(0),
                "school": school,
                "start_pos": match.start(),
                "end_pos": match.end()
            })
    
    return results


def extract_company_heuristic(text: str) -> List[Dict]:
    """
    Extrait les entreprises avec patterns heuristiques.
    """
    results = []
    
    for pattern in COMPANY_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            company = match.group("company").strip()
            results.append({
                "raw": match.group(0),
                "company": company,
                "start_pos": match.start(),
                "end_pos": match.end()
            })
    
    return results


def normalize_date_range(date_str: str) -> str:
    """
    Normalise une plage de dates.
    
    Examples:
        "2020-2023" -> "2020 – 2023"
        "S2 2023" -> "S2 2023"
        "depuis 2020" -> "2020 – Présent"
    """
    # Normaliser les tirets
    date_str = re.sub(r'\s*[-–—]\s*', ' – ', date_str)
    
    # Normaliser "Présent"
    date_str = re.sub(r'(?i)\b(actuel|actuellement|aujourd\'?hui)\b', 'Présent', date_str)
    
    return date_str


def validate_formation(formation: Dict) -> bool:
    """
    Valide qu'une formation extraite est cohérente.
    """
    etablissement = formation.get("etablissement", "")
    diplome = formation.get("diplome", "")
    
    # Vérifier qu'on a au moins un des deux
    if not etablissement and not diplome:
        return False
    
    # Vérifier que l'établissement ressemble à une école
    if etablissement:
        etab_lower = etablissement.lower()
        has_school_keyword = any(kw in etab_lower for kw in SCHOOL_KEYWORDS)
        if not has_school_keyword and len(etablissement) < 3:
            return False
    
    return True


def validate_experience(experience: Dict) -> bool:
    """
    Valide qu'une expérience extraite est cohérente.
    """
    entreprise = experience.get("entreprise", "")
    poste = experience.get("poste", "")
    
    # Vérifier qu'on a au moins l'entreprise
    if not entreprise:
        return False
    
    # Filtrer les faux positifs connus
    entreprise_lower = entreprise.lower()
    false_positives = ["projets", "projet", "compétences", "langues", "formations", 
                       "expériences", "intérêts", "loisirs", "contact"]
    if entreprise_lower in false_positives:
        return False
    
    return True


def merge_ner_and_heuristic(ner_entities: List[Dict], heuristic_entities: List[Dict]) -> List[Dict]:
    """
    Fusionne les entités NER et heuristiques, en privilégiant les heuristiques
    pour les patterns structurés.
    """
    merged = []
    ner_positions = set()
    
    # Ajouter d'abord les entités heuristiques (plus fiables pour les patterns)
    for h_ent in heuristic_entities:
        merged.append(h_ent)
        ner_positions.add(h_ent.get("start_pos", -1))
    
    # Ajouter les entités NER qui ne chevauchent pas
    for n_ent in ner_entities:
        n_start = n_ent.get("start", -1)
        overlap = False
        for h_ent in heuristic_entities:
            h_start = h_ent.get("start_pos", -1)
            h_end = h_ent.get("end_pos", -1)
            if h_start <= n_start <= h_end:
                overlap = True
                break
        if not overlap:
            merged.append(n_ent)
    
    return merged


# =============================================================================
# STRUCTURATION TEMPORELLE DES SECTIONS
# =============================================================================

def sort_by_date(items: List[Dict], date_key: str = "dates", descending: bool = True) -> List[Dict]:
    """
    Trie une liste d'items par date.
    
    Args:
        items: Liste de dicts avec une clé date
        date_key: Nom de la clé contenant la date
        descending: True pour ordre anti-chronologique
    """
    def extract_year(date_str):
        if not date_str:
            return 0
        # Trouver la première année
        match = re.search(r'(19|20)\d{2}', str(date_str))
        if match:
            return int(match.group(0))
        return 0
    
    return sorted(items, key=lambda x: extract_year(x.get(date_key, "")), reverse=descending)


def group_by_year(items: List[Dict], date_key: str = "dates") -> Dict[str, List[Dict]]:
    """
    Groupe les items par année.
    """
    groups = {}
    
    for item in items:
        date_str = item.get(date_key, "")
        match = re.search(r'(19|20)\d{2}', str(date_str))
        year = match.group(0) if match else "Autre"
        
        if year not in groups:
            groups[year] = []
        groups[year].append(item)
    
    return groups


# =============================================================================
# INTERFACE PRINCIPALE
# =============================================================================

def extract_structured_cv_data(text: str) -> Dict:
    """
    Extrait toutes les données structurées d'un CV en combinant NER et heuristiques.
    
    Returns:
        Dict avec: dates, job_titles, diplomas, schools, companies
    """
    return {
        "dates": extract_dates_heuristic(text),
        "job_titles": extract_job_title_heuristic(text),
        "diplomas": extract_diploma_heuristic(text),
        "schools": extract_school_heuristic(text),
        "companies": extract_company_heuristic(text),
    }


if __name__ == "__main__":
    # Test rapide
    test_text = """
    Léo WEBER
    leo.weber@epita.fr
    
    Formation
    EPITA : Dernière année du cycle ingénieur (Kremlin-Bicêtre)
    Lycée Hoche : Baccalauréat S mention assez bien (Versailles)
    
    Expériences
    S3 2024 – 2025 Rhine-Waal University, Allemagne
    - Programme d'échange en data science
    
    S2 2023 Paris
    - Stage de 18 semaines chez I NETUM en tant que développeur ABAP
    """
    
    result = extract_structured_cv_data(test_text)
    
    print("=== DATES ===")
    for d in result["dates"]:
        print(f"  {d}")
    
    print("\n=== DIPLÔMES ===")
    for d in result["diplomas"]:
        print(f"  {d}")
    
    print("\n=== ÉCOLES ===")
    for s in result["schools"]:
        print(f"  {s}")
    
    print("\n=== POSTES ===")
    for j in result["job_titles"]:
        print(f"  {j}")
    
    print("\n=== ENTREPRISES ===")
    for c in result["companies"]:
        print(f"  {c}")
