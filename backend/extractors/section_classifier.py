import re

SECTION_HEADERS = {
    "EXPERIENCES": [
        r"^expériences?$",
        r"^experience professionnelle",
        r"^professional experience",
        r"^parcours professionnel",
        r"^expériences professionnelles"
    ],

    "FORMATIONS": [
        r"^formations?$",
        r"^education$",
        r"^dipl[oô]mes?$",
        r"^parcours académique"
    ],

    "COMPETENCES": [
        r"^compétences?$",
        r"^skills$",
        r"^expertise$",
        r"^compétences techniques",
        r"^compétences fonctionnelles",
        
    ],

    "LANGUES": [
        r"^langues?$",
        r"^languages?$",
        r"^langue\(s\)$"
    ]
}


def detect_section_title(line: str):

    clean = line.lower().strip()

    # On enlève les ":" éventuels
    clean = clean.replace(":", "").strip()

    for section, patterns in SECTION_HEADERS.items():
        for pattern in patterns:
            if re.match(pattern, clean):
                return section

    return None


def split_by_sections(texte: str):

    sections = {
        "EXPERIENCES": "",
        "FORMATIONS": "",
        "COMPETENCES": "",
        "LANGUES": "",
        "AUTRES": ""
    }

    current = "AUTRES"

    for raw_line in texte.split("\n"):
        line = raw_line.strip()

        if not line:
            continue

        detected = detect_section_title(line)

        if detected:
            current = detected
            continue

        # Détection intelligente des langues au milieu du texte
        if re.match(r"^(français|anglais|espagnol|allemand|italien|arabe)", line.lower()):
            sections["LANGUES"] += raw_line + "\n"
            continue

        # Détection heuristique des compétences si mots clés
        if re.search(r"(java|python|react|angular|sql|jira|scrum|agile)", line.lower()):
            sections["COMPETENCES"] += raw_line + "\n"
            continue

        sections[current] += raw_line + "\n"

    return sections


def extraire_par_sections(texte: str):

    sections = split_by_sections(texte)

    return {
        "experiences_text": sections.get("EXPERIENCES", ""),
        "formations_text": sections.get("FORMATIONS", ""),
        "competences_text": sections.get("COMPETENCES", ""),
        "langues_text": sections.get("LANGUES", ""),
        "autres_text": sections.get("AUTRES", "")
    }
