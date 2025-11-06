import spacy
import re
import logging

# Configuration simple du logging pour voir les messages de débogage
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [spacy_extractor] - %(message)s')

# Charge le modèle de langue français
nlp = spacy.load("fr_core_news_md")

# Liste de mots souvent mal classifiés comme des noms de personnes (PER)
NAME_STOP_WORDS = {"langues", "compétences", "competences", "profil", "formations", "formation", "expériences", "experiences", "projets", "divers", "contact"}


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

    logging.info("Début de l'extraction des entités avec spaCy...")
    # --- Extraction SpaCy classique ---
    for ent in doc.ents:
        # Log de chaque entité trouvée par spaCy pour le débogage
        logging.info(f"  -> Entité trouvée: '{ent.text.strip()}' | Label: {ent.label_}")

        if ent.label_ == "PER":
            entites["noms"].append(ent.text)
        elif ent.label_ == "ORG":
            entites["organisations"].append(ent.text)
        elif ent.label_ == "LOC":
            entites["lieux"].append(ent.text)

    logging.info("Extraction spaCy terminée.")

    # --- Fallback : détection d’organisations par motif texte ---
    org_patterns = re.findall(
        r"(Université\s+[A-Z][A-Za-z0-9éèêëàâäçîïôöùûü\s\-]+|"
        r"Entreprise\s*:?[\sA-Z][A-Za-z0-9éèêëàâäçîïôöùûü\s\-]+|"
        r"Sopra Steria|DevCorp|ServeurPlus|EntrepriseX)",
        texte,
        flags=re.IGNORECASE
    )

    logging.info("Recherche de motifs d'organisation (fallback)...")
    for org in org_patterns:
        org_clean = org.strip(" :-\n\t")
        if org_clean and org_clean not in entites["organisations"]:
            entites["organisations"].append(org_clean)

    # --- Post-traitement : Nettoyage des noms de personnes ---
    # Retire les faux positifs comme "Langues", "Compétences", etc.
    entites["noms"] = [nom for nom in entites["noms"] if nom.lower().strip() not in NAME_STOP_WORDS]

    # --- Nettoyage et déduplication ---
    for k in entites:
        unique = []
        for x in entites[k]:
            x = x.strip()
            if x and x not in unique:
                unique.append(x)
        entites[k] = unique

    return entites
