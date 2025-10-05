import os
from pathlib import Path
from typing import List
from backend.extractors.pdf_to_docx import convert_pdf_to_docx
from analyser_cv import lire_cv_docx, extraire_dates, extraire_email, extraire_telephone, extraire_adresse
import json

def find_pdf_files(input_dir: str) -> List[Path]:
    """
    Recherche tous les fichiers PDF dans le répertoire d'entrée
    
    Args:
        input_dir (str): Chemin vers le répertoire d'entrée
    
    Returns:
        List[Path]: Liste des chemins des fichiers PDF trouvés
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Le répertoire {input_dir} n'existe pas")
        return []
        
    pdf_files = list(input_path.glob("*.pdf"))
    if not pdf_files:
        print(f"Aucun fichier PDF trouvé dans {input_dir}")
        return []
        
    print(f"{len(pdf_files)} fichier(s) PDF trouvé(s) dans {input_dir}")
    return pdf_files

def process_pdf_cv(pdf_path: str, output_json_path: str = None) -> bool:
    """
    Traite un CV au format PDF en le convertissant d'abord en DOCX puis en extrait les informations
    
    Args:
        pdf_path (str): Chemin vers le fichier PDF à traiter
        output_json_path (str): Chemin pour le fichier JSON de sortie (optionnel)
    
    Returns:
        bool: True si le traitement est réussi, False sinon
    """
    try:
        # Création du chemin pour le fichier Word temporaire
        pdf_file = Path(pdf_path)
        temp_docx = pdf_file.parent / f"{pdf_file.stem}_temp.docx"
        
        print(f"Conversion du PDF en Word: {pdf_path}")
        
        # Conversion du PDF en Word
        if not convert_pdf_to_docx(pdf_path, str(temp_docx)):
            print("Échec de la conversion PDF vers Word")
            return False
            
        print(f"Fichier Word temporaire créé: {temp_docx}")
        
        # Si output_json_path n'est pas spécifié, on le crée à partir du nom du PDF
        if output_json_path is None:
            output_json_path = str(pdf_file.parent.parent / 'output' / f'{pdf_file.stem}_resultats.json')
        
        # Extraction des données depuis le fichier Word
        print("Extraction des données du CV...")
        try:
            # Lit le contenu du CV
            texte_cv = lire_cv_docx(str(temp_docx))
            
            # Extrait les informations
            resultats = {
                "dates": extraire_dates(texte_cv),
                "emails": extraire_email(texte_cv),
                "telephones": extraire_telephone(texte_cv),
                "adresses": extraire_adresse(texte_cv)
            }
            
            # Sauvegarde les résultats
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(resultats, f, ensure_ascii=False, indent=2)
            
            success = True
            
            # Affiche les résultats
            print("\nRésultats trouvés :")
            print("-" * 20)
            print(f"Dates : {resultats['dates']}")
            print(f"Emails : {resultats['emails']}")
            print(f"Téléphones : {resultats['telephones']}")
            print(f"Adresses : {resultats['adresses']}")
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des données: {str(e)}")
            success = False
        
        # Suppression du fichier Word temporaire
        if temp_docx.exists():
            os.remove(temp_docx)
            print("Fichier Word temporaire supprimé")
            
        if success:
            print(f"Traitement terminé avec succès. Résultats sauvegardés dans: {output_json_path}")
        else:
            print("Échec de l'extraction des données")
            
        return success
        
    except Exception as e:
        print(f"Erreur lors du traitement: {str(e)}")
        return False

def process_all_pdfs(input_dir: str = "data/input", output_dir: str = "data/output") -> None:
    """
    Traite tous les fichiers PDF trouvés dans le répertoire d'entrée
    
    Args:
        input_dir (str): Chemin vers le répertoire contenant les PDF
        output_dir (str): Chemin vers le répertoire de sortie pour les JSON
    """
    # Recherche des fichiers PDF
    pdf_files = find_pdf_files(input_dir)
    if not pdf_files:
        return
    
    # Création du répertoire de sortie s'il n'existe pas
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Traitement de chaque fichier PDF
    successful = 0
    for pdf_file in pdf_files:
        print(f"\nTraitement de: {pdf_file.name}")
        output_json = output_path / f"{pdf_file.stem}_resultats.json"
        
        if process_pdf_cv(str(pdf_file), str(output_json)):
            successful += 1
            
    # Résumé final
    print(f"\nRésumé du traitement:")
    print(f"- Fichiers traités: {len(pdf_files)}")
    print(f"- Succès: {successful}")
    print(f"- Échecs: {len(pdf_files) - successful}")

if __name__ == "__main__":
    # Traitement de tous les PDF dans le dossier input
    process_all_pdfs()