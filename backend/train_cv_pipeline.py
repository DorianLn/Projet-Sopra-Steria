"""
Script d'entraînement unifié pour les composants spaCy apprenables (NER + TextCategorizer).

Ce script:
1. Entraîne le NER avec les données annotées orientées CV
2. Entraîne le TextCategorizer pour la classification de sections
3. Sauvegarde les modèles entraînés séparément
4. Génère un rapport d'entraînement

Usage:
    python train_cv_pipeline.py [--ner-iter 30] [--textcat-iter 20] [--output models/cv_pipeline]
"""

import os
import sys
import random
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from training.training_data import (
    NER_TRAINING_DATA, 
    TEXTCAT_TRAINING_DATA,
    SECTION_CATEGORIES,
    validate_training_data, 
    get_ner_labels
)


class CVPipelineTrainer:
    """Entraîneur unifié pour le pipeline CV (NER + TextCat)."""
    
    def __init__(self, base_model: str = "fr_core_news_md"):
        self.base_model = base_model
        self.ner_model = None
        self.textcat_model = None
        self.training_stats = {
            "ner": {"losses": [], "examples": 0},
            "textcat": {"losses": [], "examples": 0}
        }
    
    def load_base_model(self) -> spacy.Language:
        """Charge le modèle de base."""
        print(f"📦 Chargement du modèle de base '{self.base_model}'...")
        try:
            nlp = spacy.load(self.base_model)
        except OSError:
            print(f"Modèle '{self.base_model}' non trouvé. Téléchargement...")
            os.system(f"python -m spacy download {self.base_model}")
            nlp = spacy.load(self.base_model)
        return nlp
    
    def train_ner(self, n_iter: int = 30, dropout: float = 0.35, output_dir: str = None) -> Tuple[spacy.Language, Dict]:
        """
        Entraîne le composant NER avec les données annotées.
        
        Args:
            n_iter: Nombre d'itérations
            dropout: Taux de dropout
            output_dir: Dossier de sortie
            
        Returns:
            Tuple (modèle entraîné, statistiques)
        """
        print("\n" + "="*60)
        print("🎯 ENTRAÎNEMENT NER")
        print("="*60)
        
        # Validation des données
        print("\n🔍 Validation des données NER...")
        errors = validate_training_data(NER_TRAINING_DATA)
        if errors:
            print(f"❌ {len(errors)} erreurs dans les données:")
            for e in errors[:5]:
                print(f"   {e}")
            raise ValueError("Données d'entraînement NER invalides")
        
        print(f"✓ {len(NER_TRAINING_DATA)} exemples NER valides")
        
        # Charger le modèle
        nlp = self.load_base_model()
        
        # Configurer le NER
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner", last=True)
        else:
            ner = nlp.get_pipe("ner")
        
        # Ajouter les labels
        print("\n🏷️ Labels NER:")
        labels = get_ner_labels()
        for label in labels:
            ner.add_label(label)
            print(f"   + {label}")
        
        # Préparer les exemples
        examples = []
        for text, annotations in NER_TRAINING_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        self.training_stats["ner"]["examples"] = len(examples)
        
        # Entraînement
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
        
        print(f"\n🚀 Entraînement NER ({n_iter} itérations)...")
        print("-" * 50)
        
        with nlp.disable_pipes(*other_pipes):
            optimizer = nlp.initialize()
            
            for iteration in range(n_iter):
                random.shuffle(examples)
                losses = {}
                
                batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    nlp.update(batch, drop=dropout, losses=losses, sgd=optimizer)
                
                loss = losses.get("ner", 0)
                self.training_stats["ner"]["losses"].append(loss)
                
                if (iteration + 1) % 5 == 0 or iteration == 0:
                    print(f"   Itération {iteration + 1:3d}/{n_iter} | Loss: {loss:.2f}")
        
        # Sauvegarder
        if output_dir:
            ner_output = Path(output_dir) / "ner"
            ner_output.mkdir(parents=True, exist_ok=True)
            nlp.to_disk(ner_output)
            print(f"\n💾 Modèle NER sauvegardé: {ner_output}")
        
        self.ner_model = nlp
        
        final_loss = self.training_stats["ner"]["losses"][-1]
        print(f"\n✅ NER entraîné | Loss finale: {final_loss:.2f}")
        
        return nlp, self.training_stats["ner"]
    
    def train_textcat(self, n_iter: int = 20, dropout: float = 0.2, output_dir: str = None) -> Tuple[spacy.Language, Dict]:
        """
        Entraîne le composant TextCategorizer pour classifier les sections CV.
        
        Args:
            n_iter: Nombre d'itérations
            dropout: Taux de dropout
            output_dir: Dossier de sortie
            
        Returns:
            Tuple (modèle entraîné, statistiques)
        """
        print("\n" + "="*60)
        print("🎯 ENTRAÎNEMENT TEXTCATEGORIZER")
        print("="*60)
        
        print(f"✓ {len(TEXTCAT_TRAINING_DATA)} exemples TextCat")
        
        # Charger le modèle
        nlp = self.load_base_model()
        
        # Configurer le TextCategorizer
        if "textcat_multilabel" in nlp.pipe_names:
            nlp.remove_pipe("textcat_multilabel")
        
        textcat = nlp.add_pipe("textcat_multilabel", last=True)
        
        # Ajouter les catégories
        print("\n🏷️ Catégories de sections:")
        for label in SECTION_CATEGORIES:
            textcat.add_label(label)
            print(f"   + {label}")
        
        # Préparer les exemples
        examples = []
        for text, annotations in TEXTCAT_TRAINING_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        self.training_stats["textcat"]["examples"] = len(examples)
        
        # Entraînement
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "textcat_multilabel"]
        
        print(f"\n🚀 Entraînement TextCat ({n_iter} itérations)...")
        print("-" * 50)
        
        with nlp.disable_pipes(*other_pipes):
            nlp.initialize(lambda: examples)
            
            for iteration in range(n_iter):
                random.shuffle(examples)
                losses = {}
                
                batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    nlp.update(batch, drop=dropout, losses=losses)
                
                loss = losses.get("textcat_multilabel", 0)
                self.training_stats["textcat"]["losses"].append(loss)
                
                if (iteration + 1) % 5 == 0 or iteration == 0:
                    print(f"   Itération {iteration + 1:3d}/{n_iter} | Loss: {loss:.4f}")
        
        # Sauvegarder
        if output_dir:
            textcat_output = Path(output_dir) / "textcat"
            textcat_output.mkdir(parents=True, exist_ok=True)
            nlp.to_disk(textcat_output)
            print(f"\n💾 Modèle TextCat sauvegardé: {textcat_output}")
        
        self.textcat_model = nlp
        
        final_loss = self.training_stats["textcat"]["losses"][-1]
        print(f"\n✅ TextCat entraîné | Loss finale: {final_loss:.4f}")
        
        return nlp, self.training_stats["textcat"]
    
    def train_all(self, ner_iter: int = 30, textcat_iter: int = 20, output_dir: str = "models/cv_pipeline") -> Dict:
        """
        Entraîne tous les composants du pipeline.
        
        Args:
            ner_iter: Itérations pour le NER
            textcat_iter: Itérations pour le TextCat
            output_dir: Dossier de sortie
            
        Returns:
            Statistiques d'entraînement complètes
        """
        start_time = datetime.now()
        
        print("\n" + "="*60)
        print("🚀 ENTRAÎNEMENT PIPELINE CV COMPLET")
        print(f"   Date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Entraîner NER
        self.train_ner(n_iter=ner_iter, output_dir=output_dir)
        
        # Entraîner TextCat
        self.train_textcat(n_iter=textcat_iter, output_dir=output_dir)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Rapport final
        print("\n" + "="*60)
        print("📊 RAPPORT D'ENTRAÎNEMENT")
        print("="*60)
        print(f"   Durée totale: {duration:.1f}s")
        print(f"   Exemples NER: {self.training_stats['ner']['examples']}")
        print(f"   Exemples TextCat: {self.training_stats['textcat']['examples']}")
        print(f"   Loss NER finale: {self.training_stats['ner']['losses'][-1]:.2f}")
        print(f"   Loss TextCat finale: {self.training_stats['textcat']['losses'][-1]:.4f}")
        print("="*60)
        
        # Sauvegarder le rapport
        report = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": float(duration),
            "base_model": self.base_model,
            "ner": {
                "iterations": ner_iter,
                "examples": self.training_stats["ner"]["examples"],
                "initial_loss": float(self.training_stats["ner"]["losses"][0]),
                "final_loss": float(self.training_stats["ner"]["losses"][-1]),
                "labels": get_ner_labels()
            },
            "textcat": {
                "iterations": textcat_iter,
                "examples": self.training_stats["textcat"]["examples"],
                "initial_loss": float(self.training_stats["textcat"]["losses"][0]),
                "final_loss": float(self.training_stats["textcat"]["losses"][-1]),
                "categories": SECTION_CATEGORIES
            }
        }
        
        report_path = Path(output_dir) / "training_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📋 Rapport sauvegardé: {report_path}")
        
        return report
    
    def test_models(self):
        """Teste les modèles entraînés avec quelques exemples."""
        print("\n" + "="*60)
        print("🧪 TEST DES MODÈLES")
        print("="*60)
        
        test_texts = [
            "Marie DUPONT est Développeuse Python chez Sopra Steria depuis 2021.",
            "2020-2023: Master Informatique à l'Université Paris-Saclay",
            "FORMATION\nEPITA : Cycle Ingénieur (2020-2025)\nLycée Hoche : Bac S mention TB",
            "EXPÉRIENCE PROFESSIONNELLE\n2021-Présent: Lead DevOps chez AWS",
        ]
        
        if self.ner_model:
            print("\n📌 Test NER:")
            for text in test_texts[:2]:
                doc = self.ner_model(text)
                ents = [(ent.text, ent.label_) for ent in doc.ents]
                print(f"   \"{text[:50]}...\"")
                print(f"   → Entités: {ents}")
        
        if self.textcat_model:
            print("\n📌 Test TextCat:")
            for text in test_texts[2:]:
                doc = self.textcat_model(text)
                cats = {k: round(v, 2) for k, v in doc.cats.items() if v > 0.3}
                print(f"   \"{text[:50]}...\"")
                print(f"   → Catégories: {cats}")


def main():
    parser = argparse.ArgumentParser(description="Entraînement du pipeline CV (NER + TextCat)")
    parser.add_argument("--ner-iter", type=int, default=30, help="Itérations NER")
    parser.add_argument("--textcat-iter", type=int, default=20, help="Itérations TextCat")
    parser.add_argument("--output", type=str, default="models/cv_pipeline", help="Dossier de sortie")
    parser.add_argument("--test", action="store_true", help="Tester après entraînement")
    parser.add_argument("--ner-only", action="store_true", help="Entraîner uniquement le NER")
    parser.add_argument("--textcat-only", action="store_true", help="Entraîner uniquement le TextCat")
    
    args = parser.parse_args()
    
    trainer = CVPipelineTrainer()
    
    if args.ner_only:
        trainer.train_ner(n_iter=args.ner_iter, output_dir=args.output)
    elif args.textcat_only:
        trainer.train_textcat(n_iter=args.textcat_iter, output_dir=args.output)
    else:
        trainer.train_all(
            ner_iter=args.ner_iter,
            textcat_iter=args.textcat_iter,
            output_dir=args.output
        )
    
    if args.test:
        trainer.test_models()


if __name__ == "__main__":
    main()
