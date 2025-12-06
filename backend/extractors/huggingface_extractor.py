import os
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

# --- Configuration du chemin vers le modèle local ---
# On construit un chemin relatif depuis l'emplacement de ce fichier
# vers le dossier du modèle.
try:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    LOCAL_MODEL_PATH = os.path.join(CURRENT_DIR, "..", "models", "named-entity-recognition")
except NameError:
    # __file__ n'est pas défini dans certains environnements interactifs
    CURRENT_DIR = os.getcwd()
    LOCAL_MODEL_PATH = os.path.join(CURRENT_DIR, "models", "named-entity-recognition")


# --- Initialisation du Pipeline NER ---
# On charge le modèle une seule fois pour éviter de le recharger à chaque appel.
ner_pipeline = None
print("Attempting to load the local Hugging Face NER model...")

if not os.path.exists(LOCAL_MODEL_PATH):
    print(f"FATAL ERROR: Model directory not found at {LOCAL_MODEL_PATH}")
    print("Please ensure the model has been downloaded correctly.")
else:
    try:
        # L'option aggregation_strategy="simple" groupe automatiquement les entités
        # comme 'B-PER' et 'I-PER' en une seule entité 'PER'.
        ner_pipeline = pipeline(
            "ner",
            model=LOCAL_MODEL_PATH,
            tokenizer=LOCAL_MODEL_PATH,
            aggregation_strategy="simple"
        )
        print("✅ Hugging Face NER pipeline loaded successfully from local path.")
    except Exception as e:
        print(f"❌ ERROR loading Hugging Face NER pipeline: {e}")


def extract_entities_with_hf(text: str) -> dict:
    """
    Extracts named entities from a given text using the pre-loaded Hugging Face NER pipeline.

    Args:
        text (str): The input text from which to extract entities.

    Returns:
        dict: A dictionary with entity groups as keys and a list of extracted values as values.
              Returns an error message if the pipeline is not available.
    """
    if not ner_pipeline:
        return {"error": "Hugging Face NER pipeline is not available or failed to load."}

    try:
        # Le pipeline retourne une liste de dictionnaires, ex:
        # [{'entity_group': 'Person_Name', 'score': 0.99, 'word': 'Dorian'}]
        entities = ner_pipeline(text)

        # On regroupe les résultats par type d'entité pour un accès facile
        grouped_entities = {}
        for entity in entities:
            group = entity['entity_group']
            word = entity['word'].strip()
            
            if group not in grouped_entities:
                grouped_entities[group] = []
            
            # Éviter les doublons si le modèle en retourne
            if word not in grouped_entities[group]:
                grouped_entities[group].append(word)

        return grouped_entities

    except Exception as e:
        print(f"An error occurred during entity extraction: {e}")
        return {"error": str(e)}

# --- Bloc de test ---
# Ce code ne s'exécute que si on lance ce fichier directement (python huggingface_extractor.py)
if __name__ == '__main__':
    print("\n--- Running a test extraction ---")
    sample_cv_text = """
    Dorian LO NEGRO
    Email: dorian.loneg@email.com Tel: 06 12 34 56 78
    Expérience professionnelle chez Sopra Steria à Toulouse.
    """
    extracted_data = extract_entities_with_hf(sample_cv_text)
    
    import json
    print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
    print("---------------------------------")
