"""
Script d'entraînement complet du pipeline CV.

Entraîne:
1. NER personnalisé (PERSON_NAME, COMPANY, SCHOOL, etc.)
2. TextCategorizer pour les sections
3. Combine les deux dans un seul modèle

Usage:
    python train_pipeline.py [--iterations 30] [--output models/cv_pipeline]
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

sys.path.insert(0, str(Path(__file__).parent.parent))

from training.training_data import (
    NER_TRAINING_DATA, 
    TEXTCAT_TRAINING_DATA,
    SECTION_CATEGORIES,
    get_ner_labels,
    validate_training_data
)


def train_full_pipeline(
    base_model: str = "fr_core_news_md",
    output_dir: str = None,
    ner_iterations: int = 30,
    textcat_iterations: int = 20,
    dropout: float = 0.35
):
    """
    Entraîne le pipeline complet (NER + TextCat).
    """
    print("=" * 60)
    print("   ENTRAÎNEMENT PIPELINE CV COMPLET")
    print("=" * 60)
    
    # Validation
    print("\n🔍 Validation des données...")
    errors = validate_training_data(NER_TRAINING_DATA)
    if errors:
        raise ValueError(f"Erreurs dans les données NER: {errors[:3]}")
    print(f"   ✓ {len(NER_TRAINING_DATA)} exemples NER valides")
    print(f"   ✓ {len(TEXTCAT_TRAINING_DATA)} exemples TextCat valides")
    
    # Charger le modèle de base
    print(f"\n📦 Chargement de '{base_model}'...")
    try:
        nlp = spacy.load(base_model)
    except OSError:
        os.system(f"python -m spacy download {base_model}")
        nlp = spacy.load(base_model)
    
    # =========================================================================
    # PHASE 1: Entraînement NER
    # =========================================================================
    print("\n" + "=" * 60)
    print("   PHASE 1: ENTRAÎNEMENT NER")
    print("=" * 60)
    
    # Configurer NER
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
    
    # Ajouter les labels NER
    ner_labels = get_ner_labels()
    print("\n🏷️ Labels NER:")
    for label in ner_labels:
        ner.add_label(label)
        print(f"   + {label}")
    
    # Préparer les exemples NER
    ner_examples = []
    for text, annotations in NER_TRAINING_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        ner_examples.append(example)
    
    # Entraîner NER
    other_pipes = [p for p in nlp.pipe_names if p != "ner"]
    
    print(f"\n🚀 Entraînement NER ({ner_iterations} itérations)...")
    with nlp.disable_pipes(*other_pipes):
        nlp.initialize(lambda: ner_examples)
        
        for i in range(ner_iterations):
            random.shuffle(ner_examples)
            losses = {}
            
            batches = minibatch(ner_examples, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                nlp.update(batch, drop=dropout, losses=losses)
            
            if (i + 1) % 10 == 0:
                print(f"   Itération {i+1:3d}: loss = {losses.get('ner', 0):.4f}")
    
    print("   ✓ NER entraîné!")
    
    # =========================================================================
    # PHASE 2: Entraînement TextCat
    # =========================================================================
    print("\n" + "=" * 60)
    print("   PHASE 2: ENTRAÎNEMENT TEXTCAT")
    print("=" * 60)
    
    # Ajouter TextCategorizer
    if "textcat_multilabel" not in nlp.pipe_names:
        textcat = nlp.add_pipe("textcat_multilabel", last=True)
    else:
        textcat = nlp.get_pipe("textcat_multilabel")
    
    print("\n🏷️ Catégories de sections:")
    for cat in SECTION_CATEGORIES:
        textcat.add_label(cat)
        print(f"   + {cat}")
    
    # Préparer les exemples TextCat
    textcat_examples = []
    for text, annotations in TEXTCAT_TRAINING_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        textcat_examples.append(example)
    
    # Entraîner TextCat
    other_pipes = [p for p in nlp.pipe_names if p != "textcat_multilabel"]
    
    print(f"\n🚀 Entraînement TextCat ({textcat_iterations} itérations)...")
    with nlp.disable_pipes(*other_pipes):
        # Re-initialiser pour textcat
        optimizer = nlp.resume_training()
        
        for i in range(textcat_iterations):
            random.shuffle(textcat_examples)
            losses = {}
            
            batches = minibatch(textcat_examples, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                nlp.update(batch, drop=dropout, losses=losses, sgd=optimizer)
            
            if (i + 1) % 5 == 0:
                print(f"   Itération {i+1:3d}: loss = {losses.get('textcat_multilabel', 0):.4f}")
    
    print("   ✓ TextCat entraîné!")
    
    # =========================================================================
    # SAUVEGARDE
    # =========================================================================
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        nlp.to_disk(output_path)
        
        meta = {
            "base_model": base_model,
            "trained_on": datetime.now().isoformat(),
            "ner_iterations": ner_iterations,
            "textcat_iterations": textcat_iterations,
            "ner_labels": ner_labels,
            "textcat_labels": SECTION_CATEGORIES,
            "ner_examples": len(NER_TRAINING_DATA),
            "textcat_examples": len(TEXTCAT_TRAINING_DATA),
            "pipeline": nlp.pipe_names
        }
        with open(output_path / "training_meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Pipeline sauvegardé dans: {output_path}")
    
    return nlp


def test_pipeline(nlp):
    """Test le pipeline complet."""
    test_texts = [
        "Marie DUPONT\n06 12 34 56 78\nmarie@email.com",
        "FORMATION\n2020-2023: Master Data Science - École Polytechnique",
        "EXPÉRIENCE PROFESSIONNELLE\nDéveloppeur Python chez Google (2019-2022)",
        "COMPÉTENCES TECHNIQUES: Python, Java, Docker, Kubernetes, AWS",
        "Langues: Français natif, Anglais courant (TOEIC 920)",
    ]
    
    print("\n" + "=" * 60)
    print("   TEST DU PIPELINE")
    print("=" * 60)
    
    for text in test_texts:
        doc = nlp(text)
        
        print(f"\n📝 Texte: {text[:50]}...")
        
        # NER
        if doc.ents:
            print("   Entités NER:")
            for ent in doc.ents:
                print(f"      [{ent.label_:12}] '{ent.text}'")
        
        # TextCat
        if doc.cats:
            sorted_cats = sorted(doc.cats.items(), key=lambda x: x[1], reverse=True)
            top = sorted_cats[0]
            print(f"   Section: {top[0]} ({top[1]:.1%})")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Entraînement pipeline CV complet")
    parser.add_argument("--ner-iter", type=int, default=30)
    parser.add_argument("--textcat-iter", type=int, default=20)
    parser.add_argument("--output", "-o", type=str, default="models/cv_pipeline")
    parser.add_argument("--test", "-t", action="store_true")
    
    args = parser.parse_args()
    
    output_dir = Path(__file__).parent.parent / args.output
    
    nlp = train_full_pipeline(
        output_dir=str(output_dir),
        ner_iterations=args.ner_iter,
        textcat_iterations=args.textcat_iter
    )
    
    if args.test:
        test_pipeline(nlp)
    
    print("\n✅ Pipeline entraîné avec succès!")


if __name__ == "__main__":
    main()
