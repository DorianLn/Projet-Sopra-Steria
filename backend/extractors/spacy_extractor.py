import spacy
import re

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
        if ent.label_ == "PER":
            entites["noms"].append(ent.text)
        elif ent.label_ == "ORG":
            entites["organisations"].append(ent.text)
        elif ent.label_ == "LOC":
            entites["lieux"].append(ent.text)
        elif ent.label_ == "DATE":
            entites["dates"].append(ent.text)

    # --- Fallback : détection d’organisations par motif texte ---
    org_patterns = re.findall(
        r"(Université\s+[A-Z][A-Za-z0-9éèêëàâäçîïôöùûü\s\-]+|"
        r"Entreprise\s*:?[\sA-Z][A-Za-z0-9éèêëàâäçîïôöùûü\s\-]+|"
        r"Sopra Steria|DevCorp|ServeurPlus|EntrepriseX)",
        texte,
        flags=re.IGNORECASE
    )

    for org in org_patterns:
        org_clean = org.strip(" :-\n\t")
        if org_clean and org_clean not in entites["organisations"]:
            entites["organisations"].append(org_clean)

    # --- Nettoyage et déduplication ---
    for k in entites:
        unique = []
        for x in entites[k]:
            x = x.strip()
            if x and x not in unique:
                unique.append(x)
        entites[k] = unique

    # --- DEBUG ---
    print("===== DEBUG entites spaCy + fallback =====")
    print(entites)
    print("==========================================")

    return entites
