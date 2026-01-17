"""
Script d'entraînement du NER spaCy personnalisé pour l'extraction de CV.

Ce script:
1. Charge le modèle fr_core_news_md existant
2. Ajoute des labels NER personnalisés (PERSON_NAME, COMPANY, SCHOOL, etc.)
3. Entraîne le NER avec les données annotées
4. Sauvegarde le modèle entraîné

Usage:
    python train_ner.py [--iterations 30] [--output models/cv_ner]
"""

import os
import sys
import random
import json
from pathlib import Path
from datetime import datetime

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.training_data import NER_TRAINING_DATA, get_ner_labels, validate_training_data
from training.generated_data import GENERATED_NER_DATA

TRAIN_DATA = NER_TRAINING_DATA + GENERATED_NER_DATA

def remove_overlapping_entities(examples):
    cleaned = []

    for text, ann in examples:
        ents = ann["entities"]

        # Trier par longueur décroissante (priorité aux spans les plus longs)
        ents = sorted(ents, key=lambda x: (x[1] - x[0]), reverse=True)

        kept = []
        occupied = set()

        for start, end, label in ents:
            overlap = False
            for i in range(start, end):
                if i in occupied:
                    overlap = True
                    break

            if not overlap:
                kept.append((start, end, label))
                for i in range(start, end):
                    occupied.add(i)

        if kept:
            cleaned.append((text, {"entities": kept}))

    return cleaned

SKILL_TECH_SET = {
    "python", "java", "javascript", "react", "node", "docker", "kubernetes",
    "sql", "aws", "azure", "git", "linux", "spark", "hadoop", "tensorflow", "pandas"
}

SKILL_FUNC_SET = {
    "scrum", "agile", "kanban", "gestion de projet", "product management",
    "conduite du changement", "analyse métier", "pilotage", "recueil du besoin"
}

def normalize_skill_labels(examples):
    normalized = []

    for text, ann in examples:
        new_ents = []

        for start, end, label in ann["entities"]:
            span = text[start:end].lower()

            if label == "SKILL":
                if any(skill in span for skill in SKILL_TECH_SET):
                    new_ents.append((start, end, "SKILL_TECH"))
                elif any(skill in span for skill in SKILL_FUNC_SET):
                    new_ents.append((start, end, "SKILL_FUNC"))
                else:
                    continue  # on supprime le SKILL non classifiable
            else:
                new_ents.append((start, end, label))

        if new_ents:
            normalized.append((text, {"entities": new_ents}))

    return normalized


def create_training_examples(nlp, training_data):
    """Convertit les données d'entraînement en objets Example spaCy."""
    examples = []
    for text, annotations in training_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        examples.append(example)
    return examples


def train_ner(
    base_model: str = "fr_core_news_md",
    output_dir: str = None,
    n_iter: int = 30,
    dropout: float = 0.35
):
    """
    Entraîne le NER avec les données annotées.
    
    Args:
        base_model: Modèle spaCy de base à utiliser
        output_dir: Dossier de sortie pour le modèle entraîné
        n_iter: Nombre d'itérations d'entraînement
        dropout: Taux de dropout
    
    Returns:
        Le modèle entraîné
    """
    # Validation des données
    print("🔍 Validation des données d'entraînement...")
    errors = validate_training_data(TRAIN_DATA)
    if errors:
        print(f"❌ {len(errors)} erreurs dans les données:")
        for e in errors[:5]:
            print(f"   {e}")
        raise ValueError("Données d'entraînement invalides")
    print(f"✓ {len(TRAIN_DATA)} exemples valides")
    
    # Charger le modèle de base
    print(f"\n📦 Chargement du modèle de base '{base_model}'...")
    try:
        nlp = spacy.load(base_model)
    except OSError:
        print(f"Modèle '{base_model}' non trouvé. Téléchargement...")
        os.system(f"python -m spacy download {base_model}")
        nlp = spacy.load(base_model)
    
    # Récupérer ou créer le composant NER
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
    
    # Ajouter les nouveaux labels
    print("\n🏷️ Ajout des labels personnalisés...")
    labels = set(get_ner_labels())

    for _, ann in GENERATED_NER_DATA:
        for _, _, label in ann["entities"]:
            labels.add(label)

    labels = sorted(labels)

    for label in labels:
        ner.add_label(label)
        print(f"   + {label}")

    
    # Préparer les exemples d'entraînement
    print("\n📚 Préparation des exemples d'entraînement...")
    shuffled_data = TRAIN_DATA.copy()
    random.shuffle(shuffled_data)

    normalized_data = normalize_skill_labels(shuffled_data)
    filtered_data = remove_overlapping_entities(normalized_data)

    examples = create_training_examples(nlp, filtered_data)
    
    # Obtenir les autres composants du pipeline à désactiver pendant l'entraînement
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    
    # Entraînement
    print(f"\n🚀 Début de l'entraînement ({n_iter} itérations)...")
    print("-" * 50)
    
    with nlp.disable_pipes(*other_pipes):
        # Initialiser le NER avec les exemples
        nlp.initialize(lambda: examples)
        
        for iteration in range(n_iter):
            random.shuffle(examples)
            losses = {}
            
            # Créer des mini-batches
            batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                nlp.update(
                    batch,
                    drop=dropout,
                    losses=losses
                )
            
            if (iteration + 1) % 5 == 0 or iteration == 0:
                print(f"   Itération {iteration + 1:3d}/{n_iter}: loss = {losses.get('ner', 0):.4f}")
    
    print("-" * 50)
    print("✓ Entraînement terminé!")
    
    # Sauvegarder le modèle
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        nlp.to_disk(output_path)
        print(f"\n💾 Modèle sauvegardé dans: {output_path}")
        
        # Sauvegarder les métadonnées
        meta = {
            "base_model": base_model,
            "trained_on": datetime.now().isoformat(),
            "iterations": n_iter,
            "labels": labels,
            "examples_count": len(filtered_data)
        }
        with open(output_path / "training_meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
    
    return nlp


def test_model(nlp, test_texts=None):
    """Teste le modèle sur des textes exemples."""
    if test_texts is None:
        test_texts = [
            "Marie DUPONT\nDéveloppeuse Python Senior\n06 12 34 56 78",
            "2020-2023: Master Informatique - Université Paris-Saclay",
            "Lead DevOps chez Amazon Web Services depuis 2021",
            "Compétences: Python, Java, Docker, Kubernetes, AWS",
            "Langues: Français (natif), Anglais (courant)"
        ]
    
    print("\n🧪 Test du modèle:")
    print("=" * 60)
    
    for text in test_texts:
        doc = nlp(text)
        print(f"\nTexte: {text[:60]}...")
        if doc.ents:
            for ent in doc.ents:
                print(f"   [{ent.label_:15}] '{ent.text}'")
        else:
            print("   (aucune entité détectée)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Entraînement du NER spaCy pour CV")
    parser.add_argument("--iterations", "-n", type=int, default=30,
                        help="Nombre d'itérations (défaut: 30)")
    parser.add_argument("--output", "-o", type=str, default="models/cv_ner",
                        help="Dossier de sortie (défaut: models/cv_ner)")
    parser.add_argument("--base-model", "-m", type=str, default="fr_core_news_md",
                        help="Modèle de base (défaut: fr_core_news_md)")
    parser.add_argument("--test", "-t", action="store_true",
                        help="Tester le modèle après entraînement")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   ENTRAÎNEMENT NER PERSONNALISÉ POUR CV")
    print("=" * 60)
    
    # Chemin absolu pour la sortie
    output_dir = Path(__file__).parent.parent / args.output
    
    # Entraînement
    nlp = train_ner(
        base_model=args.base_model,
        output_dir=str(output_dir),
        n_iter=args.iterations
    )
    
    # Test si demandé
    if args.test:
        test_model(nlp)
    
    print("\n✅ Terminé!")


if __name__ == "__main__":
    main()
