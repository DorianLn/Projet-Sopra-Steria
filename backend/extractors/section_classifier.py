import re
from typing import List, Optional, Tuple
from backend.extractors.spacy_extractor import extraire_entites
import dateparser

# (Garde tes mots-clés / STOP_ORG comme avant)
FORMATION_KEYWORDS = ["université", "universite", "école", "ecole", "diplôme", "diplome",
                      "master", "licence", "bachelor", "ingénieur", "ingenieur", "iut"]
EXPERIENCE_KEYWORDS = ["stage", "alternance", "développeur", "developpeur",
                       "chef de projet", "consultant", "expérience", "experience",
                       "ingénieur", "ingenieur", "manager", "stagiaire", "mission"]
STOP_ORG = {"assoc", "association", "leadership", "club", "projets", "projet", "volontariat"}

COMPETENCE_KEYWORDS = [
    "python", "java", "javascript", "react", "docker", "sql", "aws", "git",
    "html", "css", "flask", "django", "linux", "node", "api", "ci/cd",
    "cloud", "communication", "gestion de projet", "leadership", "autonomie"
]

LANGUES_KEYWORDS = [
    "français", "anglais", "espagnol", "allemand", "italien", "portugais"
]


# ---------------------
# 1) extraire toutes les dates avec leurs positions (spans) dans le texte
# ---------------------
DATE_REGEXES = [
    r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',        # 06/2016 or 01-01-2016
    r'\b\d{1,2}[\/\-]\d{4}\b',                      # 06/2016
    r'\b(?:19|20)\d{2}\b',                          # 2016, 2019
    r'\b(?:Janvier|Février|Fevrier|Mars|Avril|Mai|Juin|Juillet|Août|Aout|Septembre|Octobre|Novembre|Décembre)\s+\d{4}\b',  # Mars 2016
    r'\b(?:\d{4})\s*[-–—]\s*(?:\d{4})\b'            # 2013-2016
]

def extraire_competences_langues(texte):
    texte_min = texte.lower()

    # Extraction des compétences
    competences_trouvees = []
    for mot in COMPETENCE_KEYWORDS:
        if re.search(rf"\b{re.escape(mot)}\b", texte_min):
            competences_trouvees.append(mot.capitalize())

    # Extraction des langues
    langues_trouvees = []
    for mot in LANGUES_KEYWORDS:
        if re.search(rf"\b{re.escape(mot)}\b", texte_min):
            langues_trouvees.append(mot.capitalize())

    return competences_trouvees, langues_trouvees

def extract_date_spans(text: str) -> List[Tuple[str,int,int,str]]:
    """
    Renvoie une liste de tuples (raw_date_text, start_idx, end_idx, normalized_iso_or_str)
    """
    spans = []
    for rx in DATE_REGEXES:
        for m in re.finditer(rx, text, flags=re.IGNORECASE):
            raw = m.group(0).strip()
            start, end = m.start(), m.end()
            # normaliser avec dateparser (peut renvoyer None si ambiguous)
            parsed = None
            try:
                # pour des plages "YYYY-YYYY" on garde raw ; sinon parse
                if re.match(r'^\d{4}\s*[-–—]\s*\d{4}$', raw):
                    parsed = raw  # on conservera la plage brute
                else:
                    dp = dateparser.parse(raw, languages=['fr'])
                    if dp:
                        # on renvoie YYYY-MM-DD si possible, sinon YYYY
                        parsed = dp.date().isoformat()
            except Exception:
                parsed = None
            spans.append((raw, start, end, parsed))
    # dédupliquer spans proches (par start)
    spans_sorted = sorted(spans, key=lambda x: x[1])
    unique = []
    seen_starts = set()
    for s in spans_sorted:
        if s[1] not in seen_starts:
            unique.append(s)
            seen_starts.add(s[1])
    return unique

# ---------------------
# 2) trouver positions d'une organisation dans le texte (toutes occurrences)
# ---------------------
def find_org_positions(org: str, text: str) -> List[Tuple[int,int]]:
    positions = []
    for m in re.finditer(re.escape(org), text, flags=re.IGNORECASE):
        positions.append((m.start(), m.end()))
    return positions

# ---------------------
# 3) associer la date la plus proche par distance caractère (fallback: sentence search)
# ---------------------
def find_closest_date_by_char(org: str, text: str, date_spans: List[Tuple[str,int,int,str]]) -> Optional[str]:
    """
    Pour une organisation, cherche la date normalisée la plus proche (par distance caractere).
    Retourne la date normalisée (parsed) ou la forme brute si pas parsée.
    """
    org_positions = find_org_positions(org, text)
    if not org_positions:
        # fallback: lowercase fuzzy match - find approximate occurrence
        # simple fallback: search first 20 chars of org
        short = org[:10].strip()
        if not short:
            return None
        # find any sentence containing short
        for m in re.finditer(re.escape(short), text, flags=re.IGNORECASE):
            org_positions.append((m.start(), m.end()))
        if not org_positions:
            return None

    best = None
    best_dist = None
    for (o_start, o_end) in org_positions:
        for raw, d_start, d_end, parsed in date_spans:
            # distance from org to date (use distance between centers)
            org_center = (o_start + o_end) / 2
            date_center = (d_start + d_end) / 2
            dist = abs(org_center - date_center)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best = parsed if parsed else raw
    return best

# ---------------------
# 4) classifier amélioré qui utilise la nouvelle association date
# ---------------------
def nettoyer_nom_organisation(org: str) -> str:
    org = re.sub(r"(?i)(entreprise|projets|compétences|competences|stage|formation)[:\s-]*", "", org)
    org = re.sub(r"\s+", " ", org)
    return org.strip(" :-\n\t")

def is_formation(org_text: str, context_text: str = "") -> bool:
    ol = org_text.lower()
    if any(k in ol for k in FORMATION_KEYWORDS):
        return True
    if any(k in context_text.lower() for k in FORMATION_KEYWORDS):
        return True
    # heuristique pour "Université" variants
    if "univ" in ol or "univers" in ol:
        return True
    return False
def nettoyer_organisations(entites_org):
    """
    Nettoie et normalise les entités d'organisations extraites par spaCy
    """
    nettoyees = []
    for org in entites_org:
        # Retire les retours à la ligne, espaces en trop, ponctuation
        org_clean = re.sub(r'[\n\r]+', ' ', org)
        org_clean = re.sub(r'\s+', ' ', org_clean).strip()

        # Coupe si plusieurs blocs séparés par des dates ou des tirets
        morceaux = re.split(r'\d{4}|\-|–|—', org_clean)
        for part in morceaux:
            part = part.strip(" -–—.,;")
            # Ignore les chaînes trop courtes ou suspectes
            if 2 < len(part) < 60 and not any(x in part.lower() for x in ["compétences", "projets", "profil"]):
                nettoyees.append(part)

    # Supprime les doublons en gardant l’ordre
    nettoyees = list(dict.fromkeys(nettoyees))
    return nettoyees

def classifier_formations_experiences(texte: str, entites: dict, dates: List[str]):
    """
    Nouvelle version : extrait date_spans, nettoie orgs, associe date la plus proche par char distance.
    """
    formations = []
    experiences = []
    date_spans = extract_date_spans(texte)  # list of (raw, start, end, normalized)
    # build a simple list of normalized strings for dedupe later
    for org in entites.get("organisations", []):
        org_clean = nettoyer_nom_organisation(org)
        if not org_clean or org_clean.lower() in STOP_ORG:
            continue
        # associe date proche
        date_assoc = find_closest_date_by_char(org_clean, texte, date_spans)
        # classification based on org name + local context (take nearby sentence)
        # get nearby sentence
        sentences = re.split(r'[.!\n]', texte)
        context = ""
        for s in sentences:
            if org_clean.lower() in s.lower():
                context = s
                break
        if is_formation(org_clean, context):
            formations.append({"etablissement": org_clean, "dates": date_assoc})
        else:
            experiences.append({"entreprise": org_clean, "dates": date_assoc})
    # deduplicate by name (keep first)
    def dedupe_list_of_dicts(l, key):
        seen = set()
        res = []
        for item in l:
            name = item.get(key, "").strip()
            if not name:
                continue
            if name not in seen:
                seen.add(name)
                res.append(item)
        return res
    formations = dedupe_list_of_dicts(formations, "etablissement")
    experiences = dedupe_list_of_dicts(experiences, "entreprise")
    return formations, experiences

# ---------------------
# 5) build_structured_json remains similar; call classifier_formations_experiences()
# ---------------------

def build_structured_json(emails, telephones, adresses, dates, texte_cv):
    entites = extraire_entites(texte_cv)
    entites["organisations"] = nettoyer_organisations(entites["organisations"])
    contact = {
        "nom": entites["noms"][0] if entites["noms"] else None,
        "email": emails[0] if emails else None,
        "telephone": telephones[0] if telephones else None,
        "adresse": adresses[0] if adresses else None
    }

    formations, experiences = classifier_formations_experiences(texte_cv, entites, dates)

    competences, langues = extraire_competences_langues(texte_cv)

    structured = {
        "contact": contact,
        "formations": formations,
        "experiences": experiences,
        "competences": list(set(entites.get("competences", []) + competences)),
        "langues": list(set(entites.get("langues", []) + langues)),
        "dates": dates
    }

    return structured
