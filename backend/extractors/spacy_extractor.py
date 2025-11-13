import spacy
import re
# Titres de sections courants à ignorer pour les noms
SECTION_TITLES = {
    "langues", "compétences", "competences", "formations",
    "expérience", "experiences", "profil", "contact", "projets"
}

def is_probable_name(text: str) -> bool:
    """Heuristique pour détecter un vrai nom (ex: Jean Martin)"""
    parts = [p for p in re.split(r"[\s\-]+", text.strip()) if p]
    if not (2 <= len(parts) <= 4):
        return False
    if any(re.search(r"\d", p) for p in parts):
        return False
    score = sum(1 for p in parts if re.match(r"^[A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ][a-zàâäçéèêëîïôöùûüÿ'\-]+$", p))
    return score >= max(2, len(parts) - 1)

# Charge le modèle de langue français
nlp = spacy.load("fr_core_news_md")

def extraire_entites(texte):
    """
    Extrait les entités (organisations, lieux, personnes, etc.) avec fallback regex
    """
    doc = nlp(texte)
    entites = {
        "noms": [],
        "organisations": [],
        "lieux": [],
        "dates": [],
        "competences": [],
        "langues": []
    }

    # --- Extraction SpaCy classique ---
    for ent in doc.ents:
        val = ent.text.strip()
        if not val:
            continue
        if ent.label_ == "PER":
            if val.lower() not in SECTION_TITLES and is_probable_name(val):
                entites["noms"].append(val)
        elif ent.label_ == "ORG":
            entites["organisations"].append(val)
        elif ent.label_ == "LOC":
            entites["lieux"].append(val)
        elif ent.label_ == "DATE":
            entites["dates"].append(val)

    # 2) Heuristique “nom en en-tête” (si spaCy n’a rien trouvé)
    if not entites["noms"]:
        # on regarde les 6 premières lignes non vides
        for line in re.split(r"[\r\n]+", texte)[:12]:
            l = line.strip(" •\t")
            if 6 <= len(l) <= 60 and l.lower() not in SECTION_TITLES and is_probable_name(l):
                entites["noms"].append(l)
                break

    # 3) Fallback ORG (universités, mots-clefs connus)
    org_patterns = re.findall(
        r"(Université\s+[A-Z][A-Za-z0-9éèêëàâäçîïôöùûü\s\-']+|"
        r"\bSopra\s*Steria\b|ServeurPlus|DevCorp|EntrepriseX|CodeForAll)",
        texte,
        flags=re.IGNORECASE
    )
    for org in org_patterns:
        org_clean = org.strip(" :-\n\t")
        if org_clean and org_clean not in entites["organisations"]:
            entites["organisations"].append(org_clean)

    for org in org_patterns:
        org_clean = org.strip(" :-\n\t")
        if org_clean and org_clean not in entites["organisations"]:
            entites["organisations"].append(org_clean)

    # 4) Nettoyage/dédoublonnage
    for k in entites:
        seen = set()
        unique = []
        for x in entites[k]:
            x = re.sub(r"\s+", " ", x).strip()
            if x and x.lower() not in SECTION_TITLES and x not in seen:
                seen.add(x)
                unique.append(x)
        entites[k] = unique

    # DEBUG (garde si utile)
    print("===== DEBUG entites spaCy + fallback =====")
    print(entites)
    print("==========================================")
    return entites
