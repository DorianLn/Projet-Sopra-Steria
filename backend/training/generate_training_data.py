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

# Chemin vers les CV analysés
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"


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
    """Valide les exemples générés."""
    valid = []
    
    for text, annotations in examples:
        entities = annotations.get("entities", [])
        all_valid = True
        
        for start, end, label in entities:
            if start < 0 or end > len(text) or start >= end:
                all_valid = False
                break
            
            # Vérifier que l'entité n'est pas vide
            entity_text = text[start:end].strip()
            if not entity_text:
                all_valid = False
                break
        
        if all_valid and entities:
            valid.append((text, annotations))
    
    return valid


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
    
    # Charger les résultats existants
    print("\n📂 Chargement des CV existants...")
    results = load_existing_results()
    print(f"   {len(results)} fichiers JSON chargés")
    
    if not results:
        print("\n⚠️ Aucun résultat trouvé. Créez d'abord des CV analysés.")
        return
    
    # Générer les exemples
    print("\n🔄 Génération des exemples...")
    examples = generate_training_data_from_results(results)
    print(f"   {len(examples)} exemples générés")
    
    # Valider
    print("\n✓ Validation...")
    valid_examples = validate_examples(examples)
    print(f"   {len(valid_examples)} exemples valides")
    
    # Exporter
    output_file = Path(__file__).parent / "generated_data.py"
    export_to_python(valid_examples, str(output_file))
    print(f"\n💾 Exporté vers: {output_file}")
    
    # Afficher quelques exemples
    print("\n📝 Exemples générés:")
    for text, ann in valid_examples[:5]:
        print(f"\n   Texte: {text[:60]}...")
        for start, end, label in ann.get("entities", []):
            print(f"      [{label}] '{text[start:end]}'")


if __name__ == "__main__":
    main()
