"""
Générateur de données d'entraînement à partir des CV existants.

Ce script:
1. Lit les fichiers JSON de sortie existants
2. Génère des exemples d'entraînement NER annotés
3. Enrichit les données d'entraînement automatiquement
"""

import os
import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

BAD_PERSON_WORDS = {
    "office", "analyst", "manager", "pack", "power", "jira", "sap", "scrum"
}

BAD_SCHOOL_WORDS = {
    "stage", "projet", "job", "mission", "intérim", "alternance"
}

CITY_WORDS = {
    "paris", "lille", "lyon", "marseille", "boston", "versailles", "douai"
}

LOCATION_CONTEXT = ["à", "au", "en", "chez", "campus", "site", "basé", "localisé", "situé"]

SKILL_TECH = {
    "python","java","javascript","react","node","sql","docker","kubernetes",
    "tensorflow","pandas","git","linux","aws","azure","spark","hadoop"
}

SHORT_SKILLS = {"c", "r", "go"}


SKILL_FUNC = {
    "gestion de projet","analyse métier","recueil du besoin","pilotage",
    "conduite du changement","scrum","agile","kanban","product management"
}

LANGUAGES = {
    "français","anglais","espagnol","allemand","italien","arabe","portugais"
}

LANG_LEVELS = {
    "a1","a2","b1","b2","c1","c2","natif","bilingue","courant","professionnel," "notions","intermédiaire","avancé", "débutant", "expert", "langue maternelle", "Lu", "Écrit", "Parlé", "notions bases"
}

def strict_filter(examples):
    seen = set()
    cleaned = []

    for text, ann in examples:
        # supprimer lignes trop longues (CV complets)
        if len(text) > 500:
            continue

        ents = ann.get("entities", [])
        valid_ents = []
        ok = True

        for s, e, label in ents:
            if s < 0 or e > len(text) or s >= e:
                ok = False
                break

            span = text[s:e].strip()
            span_low = span.lower()

            # PERSON_NAME doit ressembler à un nom
            if label == "PERSON_NAME":
                if any(w in span_low for w in BAD_PERSON_WORDS):
                    ok = False
                if len(span.split()) > 3:
                    ok = False

            # COMPANY pas trop long
            if label == "COMPANY":
                if any(w in span_low for w in ["caisse", "rayon", "stage", "mission"]):
                    ok = False

            # SCHOOL ne doit pas contenir des mots d'activité
            if label == "SCHOOL":
                if any(w in span_low for w in BAD_SCHOOL_WORDS):
                    ok = False

            # DIPLOMA ne doit pas contenir de villes
            if label == "DIPLOMA":
                if any(w in span_low for w in BAD_SCHOOL_WORDS):
                    ok = False
                if any(city in span_low for city in CITY_WORDS):
                    ok = False

            # DATE_RANGE doit contenir des chiffres
            if label == "DATE_RANGE":
                if not re.search(r"\d", span):
                    ok = False

            # JOB_TITLE pas trop long
            if label == "JOB_TITLE":
                if len(span.split()) > 5:
                    ok = False

            # LOCATION doit être dans un contexte
            if label == "LOCATION":
                if not any(ctx in text.lower() for ctx in LOCATION_CONTEXT):
                    ok = False   

            # SKILL_TECH pas trop long
            if label == "SKILL_TECH" and len(span.split()) > 3:
                ok = False

            # SKILL_FUNC pas trop long
            if label == "SKILL_FUNC" and len(span.split()) > 5:
                ok = False

            # SKILL_FUNC pas de métiers
            if label == "SKILL_FUNC" and span_low in {"développeur","engineer","manager"}:
                ok = False

            # LANGUAGE pas trop long
            if label == "LANGUAGE" and span_low == "langues":
                if len(span.split()) > 2:
                    ok = False     

            # LANG_LEVEL doit être valide   
            if label == "LANG_LEVEL" and span_low not in LANG_LEVELS:
                ok = False

            valid_ents.append((s, e, label))

        if not ok or not valid_ents:
            continue

        key = (text, tuple(valid_ents))
        if key in seen:
            continue
        seen.add(key)

        cleaned.append((text, {"entities": valid_ents}))

    return cleaned

# Chemin vers les CV analysés
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"

NER_PATTERNS = {
    "EMAIL": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
    "PHONE": r"(\+33|0)[1-9](?:[\s.-]?\d{2}){4}",
    "DATE_RANGE": r"(Depuis\s+\d{4}|\b(19|20)\d{2}\s*[–-]\s*(19|20)\d{2}\b|\bS\d\s*(19|20)\d{2}\b)",
    "LOCATION": r"\b(Paris|Lyon|Versailles|Lille|Marseille|Boston|France|Allemagne)\b",
}

ALLOWED_LABELS = {
    "PERSON_NAME", "EMAIL", "PHONE", "LOCATION",
    "COMPANY", "JOB_TITLE", "SCHOOL", "DIPLOMA", "DATE_RANGE","SKILL_TECH","SKILL_FUNC","LANGUAGE","LANG_LEVEL"
}

def clean_examples(examples):
    seen = set()
    cleaned = []

    for text, ann in examples:
        ents = []
        for start, end, label in ann["entities"]:
            if label in ALLOWED_LABELS:
                ents.append((start, end, label))

        if not ents:
            continue

        key = (text, tuple(ents))
        if key in seen:
            continue

        seen.add(key)
        cleaned.append((text, {"entities": ents}))

    return cleaned

def load_existing_results() -> List[Dict[str, Any]]:
    """Charge tous les résultats JSON existants."""
    results = []
    
    if not OUTPUT_DIR.exists():
        print(f"Dossier {OUTPUT_DIR} non trouvé")
        return results
    
    for json_file in OUTPUT_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["_source_file"] = json_file.name
                results.append(data)
        except Exception as e:
            print(f"Erreur lecture {json_file}: {e}")
    
    return results

def generate_from_raw_cvs(raw_dir="training/raw_cvs"):
    import fitz
    from docx import Document

    examples = []

    for path in Path(raw_dir).glob("*"):
        if path.suffix == ".pdf":
            text = "\n".join(p.get_text() for p in fitz.open(path))
        elif path.suffix == ".docx":
            text = "\n".join(p.text for p in Document(path).paragraphs)
        else:
            continue

        text = text.replace("\xa0", " ").replace("–", "-")

        for line in text.splitlines():
            ents = []
            line_low = line.lower()

            # Patterns classiques
            for label, pattern in NER_PATTERNS.items():
                for m in re.finditer(pattern, line):
                    ents.append((m.start(), m.end(), label))

            # Skills techniques
            for skill in SKILL_TECH:
                for m in re.finditer(rf"\b{re.escape(skill)}\b", line_low):
                    ents.append((m.start(), m.end(), "SKILL_TECH"))

            # Short skills
            for skill in SHORT_SKILLS:
                for m in re.finditer(rf"(?<!\w){skill}(?!\w)", line_low):
                    ents.append((m.start(), m.end(), "SKILL_TECH"))

            # Skills fonctionnels
            for skill in SKILL_FUNC:
                for m in re.finditer(rf"\b{re.escape(skill)}\b", line_low):
                    ents.append((m.start(), m.end(), "SKILL_FUNC"))

            # Langues
            for lang in LANGUAGES:
                for m in re.finditer(rf"\b{re.escape(lang)}\b", line_low):
                    ents.append((m.start(), m.end(), "LANGUAGE"))

            # Niveaux de langue
            for lvl in LANG_LEVELS:
                for m in re.finditer(rf"(?<!\w){re.escape(lvl)}(?!\w)", line_low):
                    ents.append((m.start(), m.end(), "LANG_LEVEL"))

            if ents:
                examples.append((line.strip(), {"entities": ents}))

    return examples


def generate_ner_example_from_header(cv_data: Dict) -> List[Tuple[str, Dict]]:
    """Génère des exemples NER depuis les données d'en-tête."""
    examples = []
    
    contact = cv_data.get("contact", {})
    nom = contact.get("nom")
    email = contact.get("email")
    telephone = contact.get("telephone")
    adresse = contact.get("adresse")
    
    if not nom:
        return examples
    
    # Construire un en-tête synthétique
    header_parts = [nom]
    if telephone:
        header_parts.append(telephone)
    if email:
        header_parts.append(email)
    if adresse:
        header_parts.append(adresse)
    
    header_text = "\n".join(header_parts)
    
    # Annoter
    entities = []
    
    # Position du nom
    nom_start = header_text.find(nom)
    if nom_start >= 0:
        entities.append((nom_start, nom_start + len(nom), "PERSON_NAME"))
    
    # Position de l'adresse
    if adresse and adresse in header_text:
        addr_start = header_text.find(adresse)
        entities.append((addr_start, addr_start + len(adresse), "LOCATION"))
    
    if entities:
        examples.append((header_text, {"entities": entities}))
    
    return examples


def generate_ner_example_from_formation(formation: Dict) -> List[Tuple[str, Dict]]:
    """Génère des exemples NER depuis une formation."""
    examples = []
    
    etablissement = formation.get("etablissement", "")
    diplome = formation.get("diplome", "")
    dates = formation.get("dates", "")
    
    if not (etablissement or diplome):
        return examples
    
    # Différents formats
    formats = []
    
    if dates and diplome and etablissement:
        formats.append(f"{dates}: {diplome} - {etablissement}")
        formats.append(f"{diplome} | {etablissement} | {dates}")
        formats.append(f"{etablissement} ({dates})\n{diplome}")
    
    for text in formats:
        entities = []
        
        if dates and dates in text:
            pos = text.find(dates)
            entities.append((pos, pos + len(dates), "DATE_RANGE"))
        
        if diplome and diplome in text:
            pos = text.find(diplome)
            entities.append((pos, pos + len(diplome), "DIPLOMA"))
        
        if etablissement and etablissement in text:
            pos = text.find(etablissement)
            entities.append((pos, pos + len(etablissement), "SCHOOL"))
        
        if entities:
            examples.append((text, {"entities": entities}))
    
    return examples


def generate_ner_example_from_experience(experience: Dict) -> List[Tuple[str, Dict]]:
    """Génère des exemples NER depuis une expérience."""
    examples = []
    
    entreprise = experience.get("entreprise", "")
    poste = experience.get("poste", "")
    dates = experience.get("dates", "")
    
    if not (entreprise or poste):
        return examples
    
    formats = []
    
    if dates and poste and entreprise:
        formats.append(f"{dates}: {poste} chez {entreprise}")
        formats.append(f"{poste} | {entreprise} | {dates}")
        formats.append(f"{entreprise} - {poste} ({dates})")
    
    for text in formats:
        entities = []
        
        if dates and dates in text:
            pos = text.find(dates)
            entities.append((pos, pos + len(dates), "DATE_RANGE"))
        
        if poste and poste in text:
            pos = text.find(poste)
            entities.append((pos, pos + len(poste), "JOB_TITLE"))
        
        if entreprise and entreprise in text:
            pos = text.find(entreprise)
            entities.append((pos, pos + len(entreprise), "COMPANY"))
        
        if entities:
            examples.append((text, {"entities": entities}))
    
    return examples


def generate_training_data_from_results(results: List[Dict]) -> List[Tuple[str, Dict]]:
    """Génère toutes les données d'entraînement."""
    all_examples = []
    
    for cv_data in results:
        # En-tête
        all_examples.extend(generate_ner_example_from_header(cv_data))
        
        # Formations
        for formation in cv_data.get("formations", []):
            all_examples.extend(generate_ner_example_from_formation(formation))
        
        # Expériences
        for experience in cv_data.get("experiences", []):
            all_examples.extend(generate_ner_example_from_experience(experience))
    
    return all_examples


def validate_examples(examples: List[Tuple[str, Dict]]) -> List[Tuple[str, Dict]]:
    valid = []

    for text, annotations in examples:
        entities = annotations.get("entities", [])
        all_valid = True

        for start, end, label in entities:
            if start < 0 or end > len(text) or start >= end:
                all_valid = False
                break

            entity_text = text[start:end].strip()
            if not entity_text:
                all_valid = False
                break

        if all_valid and entities:
            valid.append((text, annotations))

    return valid


def filter_bad_examples(examples):
    filtered = []
    for text, ann in examples:
        ents = ann["entities"]

        # supprimer chevauchements
        spans = [(s, e) for s, e, _ in ents]
        if len(spans) != len(set(spans)):
            continue

        # supprimer entreprise = job
        if "chez Product Owner" in text:
            continue

        # supprimer noms trop longs
        if any(label == "PERSON_NAME" and len(text[start:end].split()) > 4 for start, end, label in ann["entities"]):
            continue

        filtered.append((text, ann))
    return filtered

def export_to_python(examples: List[Tuple[str, Dict]], output_file: str):
    """Exporte les exemples en format Python."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Données d'entraînement générées automatiquement\n\n")
        f.write("GENERATED_NER_DATA = [\n")
        
        for text, annotations in examples:
            # Échapper les caractères
            text_escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            
            f.write(f'    (\n')
            f.write(f'        "{text_escaped}",\n')
            f.write(f'        {{"entities": {annotations.get("entities", [])}}}\n')
            f.write(f'    ),\n')
        
        f.write("]\n")


def main():
    print("=" * 60)
    print("GÉNÉRATION DE DONNÉES D'ENTRAÎNEMENT")
    print("=" * 60)

    all_examples = []

    # 1) Depuis CV bruts
    print("\n📂 Lecture des CV bruts...")
    raw_examples = generate_from_raw_cvs()
    print(f"   {len(raw_examples)} exemples depuis CV bruts")
    all_examples.extend(raw_examples)

    # 2) Depuis JSON existants
    print("\n📂 Lecture des JSON existants...")
    results = load_existing_results()
    print(f"   {len(results)} fichiers JSON chargés")

    if results:
        json_examples = generate_training_data_from_results(results)
        print(f"   {len(json_examples)} exemples depuis JSON")
        all_examples.extend(json_examples)

    # Validation
    print("\n✓ Validation...")
    valid_examples = validate_examples(all_examples)
    valid_examples = filter_bad_examples(valid_examples)
    valid_examples = strict_filter(valid_examples)
    print(f"   {len(valid_examples)} exemples valides après filtre strict")
    # Nettoyage
    print("\n🧹 Nettoyage...")
    cleaned = clean_examples(valid_examples)
    print(f"   {len(cleaned)} exemples après nettoyage")

    # Export
    output_file = Path(__file__).parent / "generated_data.py"
    export_to_python(cleaned, str(output_file))
    print(f"\n💾 Exporté vers: {output_file}")

    # Afficher quelques exemples
    print("\n📝 Exemples générés:")
    for text, ann in cleaned[:5]:
        print(f"\n   Texte: {text[:60]}...")
        for start, end, label in ann.get("entities", []):
            print(f"      [{label}] '{text[start:end]}'")


if __name__ == "__main__":
    main()


