"""
Script pour extraire les informations d'un CV
"""
import os
import json
from docx import Document
from backend.extractors.extracteur import extraire_dates, extraire_email, extraire_telephone

def lire_cv_docx(chemin_fichier):
    """Lit le contenu d'un fichier .docx"""
    doc = Document(chemin_fichier)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def analyser_cv():
    # Chemins des dossiers
    dossier_input = "data/input"
    dossier_output = "data/output"
    
    # Assure que le dossier output existe
    os.makedirs(dossier_output, exist_ok=True)
    
    # Cherche les fichiers .docx dans le dossier input
    fichiers_cv = [f for f in os.listdir(dossier_input) if f.endswith('.docx')]
    
    if not fichiers_cv:
        print("Aucun CV (.docx) trouvé dans le dossier data/input")
        return
    
    for fichier in fichiers_cv:
        print(f"\nAnalyse du CV : {fichier}")
        chemin_cv = os.path.join(dossier_input, fichier)
        
        # Lit le contenu du CV
        texte_cv = lire_cv_docx(chemin_cv)
        
        # Extrait les informations
        resultats = {
            "dates": extraire_dates(texte_cv),
            "emails": extraire_email(texte_cv),
            "telephones": extraire_telephone(texte_cv)
        }
        
        # Crée le nom du fichier de sortie
        nom_fichier_sortie = os.path.splitext(fichier)[0] + "_resultats.json"
        chemin_sortie = os.path.join(dossier_output, nom_fichier_sortie)
        
        # Sauvegarde les résultats
        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, ensure_ascii=False, indent=2)
        
        # Affiche les résultats
        print("\nRésultats trouvés :")
        print("-" * 20)
        print(f"Dates : {resultats['dates']}")
        print(f"Emails : {resultats['emails']}")
        print(f"Téléphones : {resultats['telephones']}")
        print(f"\nRésultats sauvegardés dans : {chemin_sortie}")

if __name__ == "__main__":
    analyser_cv()