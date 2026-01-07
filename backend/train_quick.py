"""
Script d'entraînement rapide du modèle NER
"""
import spacy
from spacy.training import Example
from training.training_data import NER_TRAINING_DATA
import random
import warnings
warnings.filterwarnings('ignore')

def train_model():
    print('Chargement du modèle de base...')
    nlp = spacy.load('fr_core_news_md')

    # Ajouter les labels personnalisés
    ner = nlp.get_pipe('ner')
    labels = ['PERSON_NAME', 'COMPANY', 'SCHOOL', 'DIPLOMA', 'JOB_TITLE', 'SKILL', 'LANGUAGE', 'DATE_RANGE', 'LOCATION']
    for label in labels:
        ner.add_label(label)

    # Préparer les données
    train_examples = []
    for text, annotations in NER_TRAINING_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        train_examples.append(example)

    print(f'{len(train_examples)} exemples préparés')

    # Entraînement
    print('Entraînement (30 itérations)...')
    optimizer = nlp.resume_training()
    for i in range(30):
        random.shuffle(train_examples)
        losses = {}
        for batch in spacy.util.minibatch(train_examples, size=8):
            nlp.update(batch, drop=0.35, losses=losses)
        if (i+1) % 5 == 0:
            print(f'  Itération {i+1}: loss = {losses.get("ner", 0):.2f}')

    # Sauvegarder
    output_path = 'models/cv_ner'
    nlp.to_disk(output_path)
    print(f'Modèle sauvegardé dans {output_path}')

    # Test
    print('\n=== Test du modèle ===')
    test_texts = [
        'Marie DUPONT est Développeuse Python chez Sopra Steria.',
        '2020-2023: Master Informatique à Polytechnique Paris.',
        'Ingénieur DevOps - Thales, Bordeaux (2019-2022)',
    ]
    
    for text in test_texts:
        print(f'\nTexte: "{text}"')
        doc = nlp(text)
        for ent in doc.ents:
            print(f'  {ent.label_}: {ent.text}')

if __name__ == "__main__":
    train_model()
