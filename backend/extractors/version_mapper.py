"""
Module de normalisation CV : conversion ancien format → format TEMPLATE Sopra Steria

APPROCHE SIMPLE ET FIDÈLE:
- Aucun parsing métier
- Aucune déduction
- Copie intégrale du contenu

Retourne un JSON avec des listes simples de strings (pas de structures métier)
"""

from typing import Dict, List, Any
from pathlib import Path
from docx import Document




def extract_from_docx(docx_path: str) -> Dict[str, Any]:
    """
    Extrait directement du DOCX en cherchant les 5 titres de sections.
    
    Retourne un Dict avec resultats_spacy pour compatibilité avec normalize_old_cv_to_new.
    
    Cette approche fonctionne mieux pour les anciens formats de CV que le pipeline classique.
    """
    
    try:
        doc = Document(docx_path)
    except Exception:
        return {}
    
    # Lire tous les paragraphes
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    # Titres des 5 sections à chercher (case-insensitive)
    section_titles = {
        "competences_fonctionnelles": ["Compétences fonctionnelles", "competences fonctionnelles"],
        "competences_techniques": ["Compétences techniques", "competences techniques"],
        "experiences": ["Expériences", "Experience", "Experiences"],
        "formations": ["Formation", "Formations", "Diplômes"],
        "langues": ["Langue", "Langues", "Langue(s)"]
    }
    
    # Trouver les positions des titres
    section_positions = {}
    for i, para in enumerate(paragraphs):
        para_lower = para.lower()
        for section, titles in section_titles.items():
            for title in titles:
                if title.lower() == para_lower:
                    section_positions[section] = i
                    break
    
    # Si on n'a trouvé aucune section, retourner vide
    if not section_positions:
        return {}
    
    # Extraire le contenu entre les titres
    sections_content = {}
    for section, start_idx in section_positions.items():
        # Trouver le prochain titre
        next_idx = len(paragraphs)
        for other_section, other_idx in section_positions.items():
            if other_idx > start_idx:
                next_idx = min(next_idx, other_idx)
        
        # Extraire les lignes entre ce titre et le suivant
        content = paragraphs[start_idx + 1:next_idx]
        # Filtrer les lignes vides
        content = [line for line in content if line]
        sections_content[section] = content
    
    # Extraire le nom du premier paragraphe (titre du CV)
    nom = paragraphs[0] if paragraphs else ""
    
    # Retourner au format attendu par normalize_old_cv_to_new
    return {
        "resultats_spacy": {
            "contact": {"nom": nom},
            "competences_fonctionnelles": sections_content.get("competences_fonctionnelles", []),
            "competences_techniques": sections_content.get("competences_techniques", []),
            "experiences": sections_content.get("experiences", []),
            "formations": sections_content.get("formations", []),
            "langues": sections_content.get("langues", [])
        }
    }


def extract_initiales(nom: str) -> str:
    """Extrait initiales du nom (e.g., 'Jean Dupont' → 'JD')."""
    if not nom:
        return ""
    parties = nom.split()
    if len(parties) >= 2:
        return f"{parties[0][0]}{parties[-1][0]}".upper()
    elif parties:
        return parties[0][0].upper()
    return ""


def extract_contact_info(old_data: Dict) -> Dict[str, str]:
    """Extrait les informations de contact (nom, email, téléphone)."""
    contact = {}
    
    # Chercher "resultats_spacy" puis "contact" direct
    spacy_data = old_data.get("resultats_spacy", {})
    contact_data = spacy_data.get("contact", {}) if spacy_data else old_data.get("contact", {})
    
    if not contact_data:
        contact_data = old_data
    
    contact["nom"] = contact_data.get("nom") or old_data.get("nom", "")
    contact["email"] = contact_data.get("email") or old_data.get("email", "")
    contact["telephone"] = contact_data.get("telephone") or old_data.get("telephone", "")
    contact["adresse"] = contact_data.get("adresse") or old_data.get("adresse", "")
    
    return contact


def group_experiences_into_blocks(experiences_lines: List[str]) -> List[Dict[str, Any]]:
    """
    Regroupe les lignes d'expériences en blocs structurés.
    
    PATTERN :
    - Ligne titre : commence par un mois (Janvier, Février, etc.) et contient " – " ou " - "
    - Lignes missions : suivent le titre jusqu'à la prochaine ligne "Environnement"
    - Ligne environnement : commence par "Environnement technique"
    
    SORTIE : Liste de dicts
    [
      {
        "titre": "Période - Entreprise – Fonction - Titre",
        "missions": ["mission1", "mission2", ...],
        "environnement": "AS400, Logiciels Carrefour, ..."
      },
      ...
    ]
    
    ACTION : Regroupement SIMPLE, pas de parsing métier.
    """
    if not experiences_lines or not isinstance(experiences_lines, list):
        return []
    
    # Mois français pour la détection des titres
    MONTHS = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ]
    
    blocks = []
    current_block = None
    
    for line in experiences_lines:
        if not line or not isinstance(line, str):
            continue
        
        line = line.strip()
        if not line:
            continue
        
        # Détection d'une ligne titre : commence par un mois ET contient un tiret
        starts_with_month = any(line.startswith(month) for month in MONTHS)
        has_dash = ' – ' in line or ' - ' in line
        is_title = starts_with_month and has_dash
        
        # Détection d'une ligne environnement
        is_environnement = line.lower().startswith('environnement technique')
        
        if is_title:
            # Nouvelle expérience : fermer le bloc précédent et en créer un nouveau
            if current_block and current_block['titre']:
                blocks.append(current_block)
            
            current_block = {
                'titre': line,
                'missions': [],
                'environnement': ''
            }
        
        elif is_environnement:
            # Ligne environnement : l'ajouter au bloc courant
            if current_block is not None:
                # Extraire la partie après "Environnement technique : "
                if ': ' in line:
                    environnement_text = line.split(': ', 1)[1]
                else:
                    environnement_text = line
                
                current_block['environnement'] = environnement_text
        
        elif current_block is not None:
            # Ligne de mission : l'ajouter au bloc courant
            current_block['missions'].append(line)
    
    # Ajouter le dernier bloc
    if current_block and current_block['titre']:
        blocks.append(current_block)
    
    return blocks


def normalize_old_cv_to_new(cv_data: Dict, docx_path: str = None) -> Dict[str, Any]:
    """
    Convertit un CV ancien format vers le JSON du template Sopra Steria
    
    APPROCHE SIMPLE ET FIDÈLE:
    - Aucun parsing métier
    - Aucune déduction
    - Copie intégrale du contenu
    
    Paramètres:
        cv_data: Dict avec structure {resultats_spacy: {contact, competences_*, experiences, formations, langues}}
                 OU données brutes du JSON
        docx_path: (optionnel) Path au fichier DOCX pour extraction directe (recommandé pour anciens formats)
    
    STRUCTURE:
    {
      "header": {...},
      "competences_fonctionnelles": ["ligne1", "ligne2", ...],
      "competences_techniques": ["ligne1", "ligne2", ...],
      "experiences": ["bloc1", "bloc2", ...],
      "formations": ["ligne1", "ligne2", ...],
      "langues": ["ligne1", "ligne2", ...]
    }
    """
    
    # Si un chemin DOCX est fourni, extraire directement du DOCX (meilleur résultat pour anciens formats)
    if docx_path and Path(docx_path).exists():
        cv_data = extract_from_docx(docx_path)
        if not cv_data.get("resultats_spacy"):
            # Si extraction DOCX échoue, continuer avec cv_data original
            pass
        else:
            # Extraction réussie, utiliser ces données
            pass
    
    # Extraction des données de base
    contact = extract_contact_info(cv_data)
    nom = contact.get("nom", "")
    initiales = extract_initiales(nom)
    
    # === HEADER ===
    header = {
        "confidentialite": "C2 - Usage restreint",
        "titre_document": "CURRICULUM VITAE",
        "role": "",
        "initiales": initiales
    }
    
    # === COMPETENCES FONCTIONNELLES (copie fidèle) ===
    competences_fonctionnelles = []
    
    # Chercher dans spacy
    spacy = cv_data.get("resultats_spacy", {})
    if "competences_fonctionnelles" in spacy and isinstance(spacy["competences_fonctionnelles"], list):
        competences_fonctionnelles.extend(spacy["competences_fonctionnelles"])
    
    # Chercher dans cv_data direct
    if "competences_fonctionnelles" in cv_data and isinstance(cv_data["competences_fonctionnelles"], list):
        competences_fonctionnelles.extend(cv_data["competences_fonctionnelles"])
    
    # Nettoyer les doublons en gardant l'ordre
    competences_fonctionnelles = list(dict.fromkeys(c for c in competences_fonctionnelles if c))
    
    # === COMPETENCES TECHNIQUES (copie fidèle) ===
    competences_techniques = []
    
    # Chercher dans spacy
    if "competences_techniques" in spacy and isinstance(spacy["competences_techniques"], list):
        competences_techniques.extend(spacy["competences_techniques"])
    
    # Chercher dans cv_data direct
    if "competences_techniques" in cv_data and isinstance(cv_data["competences_techniques"], list):
        competences_techniques.extend(cv_data["competences_techniques"])
    
    # Nettoyer
    competences_techniques = list(dict.fromkeys(c for c in competences_techniques if c))
    
    # === EXPERIENCES (regroupées en blocs : titre + missions + environnement) ===
    experiences_lines = []
    
    if "experiences" in spacy and isinstance(spacy["experiences"], list):
        # Les expériences du format spacy sont des strings ou des listes
        for exp in spacy["experiences"]:
            if isinstance(exp, str) and exp.strip():
                experiences_lines.append(exp.strip())
            elif isinstance(exp, list):
                # Si c'est une liste, la concaténer
                experiences_lines.extend(str(e).strip() for e in exp if e)
    
    if "experiences" in cv_data and isinstance(cv_data["experiences"], list):
        for exp in cv_data["experiences"]:
            if isinstance(exp, str) and exp.strip():
                experiences_lines.append(exp.strip())
            elif isinstance(exp, list):
                experiences_lines.extend(str(e).strip() for e in exp if e)
    
    # Déduplique
    experiences_lines = list(dict.fromkeys(experiences_lines))
    
    # Regrouper en blocs structurés
    experiences = group_experiences_into_blocks(experiences_lines)
    
    # === FORMATIONS (copie fidèle) ===
    formations = []
    
    if "formations" in spacy and isinstance(spacy["formations"], list):
        for form in spacy["formations"]:
            if isinstance(form, str) and form.strip():
                formations.append(form.strip())
            elif isinstance(form, list):
                formations.extend(str(f).strip() for f in form if f)
    
    if "formations" in cv_data and isinstance(cv_data["formations"], list):
        for form in cv_data["formations"]:
            if isinstance(form, str) and form.strip():
                formations.append(form.strip())
            elif isinstance(form, list):
                formations.extend(str(f).strip() for f in form if f)
    
    formations = list(dict.fromkeys(formations))
    
    # === LANGUES (copie fidèle) ===
    langues = []
    
    if "langues" in spacy and isinstance(spacy["langues"], list):
        for lang in spacy["langues"]:
            if isinstance(lang, str) and lang.strip():
                langues.append(lang.strip())
    
    if "langues" in cv_data and isinstance(cv_data["langues"], list):
        for lang in cv_data["langues"]:
            if isinstance(lang, str) and lang.strip():
                langues.append(lang.strip())
    
    langues = list(dict.fromkeys(langues))
    
    # === CONSTRUCTION FINALE (STRUCTURE TEMPLATE SOPRA STERIA) ===
    return {
        "contact": {"nom": nom},
        "header": header,
        "competences_fonctionnelles": competences_fonctionnelles,
        "competences_techniques": competences_techniques,
        "experiences": experiences,
        "formations": formations,
        "langues": langues
    }


def convert_v2_to_old_format(cv_template: Dict) -> Dict[str, Any]:
    """
    Convertit le format template Sopra vers le format ancien pour compatibilité avec generate_sopra_docx.
    
    Entrée:
        cv_template: Dict au format template Sopra (sortie de normalize_old_cv_to_new)
        Structure: {header, competences_fonctionnelles[], competences_techniques[], experiences[], formations[], langues[]}
    
    Sortie:
        Dict compatible avec le pipeline ancien (generate_sopra_docx, docx_to_pdf)
        Structure: {contact, competences[], experiences[], formations[], langues[], certifications[], loisirs[]}
    """
    
    # Extraction basique
    header = cv_template.get("header", {})
    if not isinstance(header, dict):
        header = {}
    
    initiales = header.get("initiales", "")
    
    # Extraire le nom depuis header ou contact
    nom = None
    if header.get("initiales"):
        nom = header.get("initiales")
    
    contact_data = cv_template.get("contact", {})
    if isinstance(contact_data, dict) and contact_data.get("nom"):
        nom = contact_data.get("nom")
    
    # Construire un nom basique depuis initiales
    nom = nom or initiales or "Candidat"
    
    # Helper pour convertir les listes en strings
    def extract_strings(value):
        """Extrait les strings d'une valeur (peut être liste, dict, string, etc)"""
        if isinstance(value, str):
            return [value] if value.strip() else []
        elif isinstance(value, dict):
            # Si c'est un dict, en extraire les valeurs et les joindre
            values = []
            for v in value.values():
                if isinstance(v, str) and v.strip():
                    values.append(v.strip())
            return values
        elif isinstance(value, (list, tuple)):
            result = []
            for item in value:
                if isinstance(item, str) and item.strip():
                    result.append(item.strip())
                elif isinstance(item, dict):
                    # Extraire les valeurs du dict
                    for v in item.values():
                        if isinstance(v, str) and v.strip():
                            result.append(v.strip())
            return result
        return []
    
    # Competences: fusionner techniques + fonctionnelles
    comp_techniques = cv_template.get("competences_techniques", [])
    comp_fonctionnelles = cv_template.get("competences_fonctionnelles", [])
    
    competences_flat = []
    for item in comp_techniques + comp_fonctionnelles:
        if isinstance(item, str) and item.strip():
            competences_flat.append(item.strip())
        elif isinstance(item, dict):
            # Si dict, extraire les valeurs pertinentes
            for v in item.values():
                if isinstance(v, str) and v.strip():
                    competences_flat.append(v.strip())
    
    # Experiences: convertir strings en structure dict pour generate_sopra_docx
    experiences = []
    exp_list = cv_template.get("experiences", [])
    
    if isinstance(exp_list, list):
        for exp in exp_list:
            if isinstance(exp, dict):
                # Déjà en format dict
                experiences.append(exp)
            elif isinstance(exp, str) and exp.strip():
                # String brut: créer une entrée dict simple
                experiences.append({
                    "dates": "",
                    "entreprise": "",
                    "poste": "",
                    "description": [exp.strip()]
                })
    
    # Formations: convertir si nécessaire
    formations = []
    form_list = cv_template.get("formations", [])
    
    if isinstance(form_list, list):
        for form in form_list:
            if isinstance(form, str) and form.strip():
                formations.append({
                    "diplome": form.strip(),
                    "annee": "",
                    "etablissement": ""
                })
            elif isinstance(form, dict):
                formations.append(form)
    
    # Langues: garder comme-is (liste de strings)
    langues = []
    lang_list = cv_template.get("langues", [])
    if isinstance(lang_list, list):
        for lang in lang_list:
            if isinstance(lang, str) and lang.strip():
                langues.append(lang.strip())
    
    # Construire le format ancien
    return {
        "contact": {
            "nom": nom,
            "email": "",
            "telephone": "",
            "adresse": ""
        },
        "experiences": experiences,
        "formations": formations,
        "competences": competences_flat,
        "langues": langues,
        "certifications": [],
        "loisirs": []
    }
