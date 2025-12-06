from transformers import AutoTokenizer, AutoModelForTokenClassification
import os

def download_model():
    """
    Downloads and saves the Hugging Face model and tokenizer to a local directory.
    """
    # The model identifier from the Hugging Face Hub
    model_name = "mdarhri00/named-entity-recognition"
    
    # The local directory where the model will be saved
    # We place it in a 'models' subfolder within the backend directory
    local_model_path = os.path.join(os.path.dirname(__file__), "models", "named-entity-recognition")

    # Create the directory if it doesn't already exist
    if not os.path.exists(local_model_path):
        os.makedirs(local_model_path)
        print(f"Created directory: {local_model_path}")

    print(f"Downloading model and tokenizer for '{model_name}'...")

    # Download and save the tokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(local_model_path)
        print("Tokenizer saved successfully.")
    except Exception as e:
        print(f"Error downloading/saving tokenizer: {e}")
        return

    # Download and save the model
    try:
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        model.save_pretrained(local_model_path)
        print("Model saved successfully.")
    except Exception as e:
        print(f"Error downloading/saving model: {e}")
        return

    print(f"Model '{model_name}' is now saved locally at: {local_model_path}")

if __name__ == "__main__":
    download_model()
