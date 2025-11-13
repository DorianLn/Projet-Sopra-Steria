import re
from typing import List, Optional, Tuple
import dateparser
from rich.console import Console
from rich.table import Table
from backend.extractors.spacy_extractor import extraire_entites

console = Console()

# ---------------------
# 0️ Mots-clés
# ---------------------
FORMATION_KEYWORDS = [
    "université", "universite", "école", "ecole", "diplôme", "diplome",
    "master", "licence", "bachelor", "ingénieur", "ingenieur", "iut"
]
EXPERIENCE_KEYWORDS = [
    "stage", "alternance", "développeur", "developpeur", "full stack",
    "chef de projet", "consultant", "expérience", "experience",
    "ingénieur", "ingenieur", "manager", "stagiaire", "mission"
]
STOP_ORG = {"assoc", "association", "leadership", "club", "projets", "projet", "volontariat"}

COMPETENCE_KEYWORDS = [
    "python", "java", "javascript", "react", "docker", "sql", "aws", "git",
    "html", "css", "flask", "django", "linux", "node", "api", "ci/cd",
    "cloud", "communication", "gestion de projet", "leadership", "autonomie"
]
LANGUES_KEYWORDS = ["français", "anglais", "espagnol", "allemand", "italien", "portugais"]

DATE_REGEXES = [
    r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
    r'\b\d{1,2}[\/\-]\d{4}\b',
    r'\b(?:19|20)\d{2}\b',
    r'\b(?:Janvier|Février|Fevrier|Mars|Avril|Mai|Juin|Juillet|Août|Aout|Septembre|Octobre|Novembre|Décembre)\s+\d{4}\b',
    r'\b(?:\d{4})\s*[-–—]\s*(?:\d{4})\b'
]

# ---------------------
# 1️ Extraction de base
# ---------------------
def extraire_competences_langues(texte):
    texte_min = texte.lower()
    competences = [m.capitalize() for m in COMPETENCE_KEYWORDS if re.search(rf"\b{re.escape(m)}\b", texte_min)]
    langues = [m.capitalize() for m in LANGUES_KEYWORDS if re.search(rf"\b{re.escape(m)}\b", texte_min)]
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

                    # 🩹 Filtrer les dates du jour (erreur fréquente de dateparser)
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


def nettoyer_organisations(entites_org):
    nettoyees = []
    for org in entites_org:
        org_clean = re.sub(r'\s+', ' ', org.strip())
        morceaux = re.split(r'(?:(?:19|20)\d{2}|[\-–—])', org_clean)
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
# 4️ Classif formation/exp avec poste
# ---------------------
def classifier_formations_experiences(texte: str, entites: dict, dates: List[str]):
    formations, experiences = [], []
    date_spans = extract_date_spans(texte)

    for org in entites.get("organisations", []):
        org_clean = nettoyer_nom_organisation(org)
        if not org_clean or org_clean.lower() in STOP_ORG:
            continue
        if org_clean.lower() in EXPERIENCE_KEYWORDS:
            continue

        # associer la date
        date_assoc = find_closest_date_by_char(org_clean, texte, date_spans)
        context = next((s for s in re.split(r'[.!\n]', texte) if org_clean.lower() in s.lower()), "")

        # détecter un poste dans le contexte proche
        poste_match = re.search(r"(développeur(?:\s+\w+){0,2}|chef de projet|consultant|ingénieur|manager)", context, re.IGNORECASE)
        poste = poste_match.group(0).capitalize() if poste_match else None

        if is_formation(org_clean, context):
            formations.append({"etablissement": org_clean, "dates": date_assoc})
        else:
            experiences.append({"entreprise": org_clean, "poste": poste, "dates": date_assoc})

    #  Correction date si None
    for item in formations + experiences:
        if item.get("dates") in (None, "", "2025-11-12"):
            match = re.search(r"(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}", texte)
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

    #  Nom
    nom = entites["noms"][0] if entites.get("noms") else None

    #  Si spaCy renvoie un nom pollué ("Thomas Dupont Développeur"), on nettoie
    if nom:
        nom = re.sub(
            r"\b(?:développeur|developer|ingénieur|consultant|manager|full\s*stack|data|web|chef)\b.*",
            "",
            nom,
            flags=re.IGNORECASE
        ).strip()

    #  Sinon on applique la logique de fallback habituelle
    if not nom:
        lignes = [l.strip() for l in texte_cv.splitlines()[:10] if len(l.strip()) > 3]
        for l in lignes:
            if re.search(r"nom\s*[:\-]", l, re.IGNORECASE):
                nom = re.sub(r"(?i)nom\s*[:\-]\s*", "", l).strip()
                break
            if re.match(r"^[A-Z][a-zà-ÿ'\-]+\s+[A-Z][A-ZÀ-Ÿ'\-]+", l):
                nom = re.sub(
                    r"\b(?:développeur|developer|ingénieur|consultant|manager|full\s*stack|data|web|chef)\b.*",
                    "",
                    l,
                    flags=re.IGNORECASE
                ).strip()
                break

    contact = {
        "nom": nom,
        "email": emails[0] if emails else None,
        "telephone": telephones[0] if telephones else None,
        "adresse": adresses[0] if adresses else None,
    }

    formations, experiences = classifier_formations_experiences(texte_cv, entites, dates)
    comp_kw, lang_kw = extraire_competences_langues(texte_cv)
    comp_sec = parse_section_competences(texte_cv)
    lang_sec = parse_section_langues(texte_cv)
    projets = parse_section_projets(texte_cv)
    certifs = parse_section_certifications(texte_cv)
    loisirs = parse_section_loisirs(texte_cv)
    dispo = parse_disponibilite(texte_cv)

    def clean_list(l):
        seen, out = set(), []
        for x in l:
            x = x.strip()
            if x and x.lower() not in seen:
                seen.add(x.lower())
                out.append(x)
        return out

    competences = clean_list(entites.get("competences", []) + comp_kw + comp_sec)
    langues = clean_list(entites.get("langues", []) + lang_kw + lang_sec)

    # 🧾 Résumé console
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

    return {
        "contact": contact,
        "formations": formations,
        "experiences": experiences,
        "competences": sorted(competences),
        "langues": sorted(langues),
        "projets": projets,
        "certifications": certifs,
        "loisirs": loisirs,
        "disponibilite": dispo,
        "dates": dates,
    }
