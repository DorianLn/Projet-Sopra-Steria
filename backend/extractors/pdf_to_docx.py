import logging
from pathlib import Path
import PyPDF2
from docx import Document
from docx.shared import Inches

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert_pdf_to_docx(pdf_path: str, docx_path: str) -> bool:
    """
    Convertit un fichier PDF en document Word (.docx)
    
    Args:
        pdf_path (str): Chemin du fichier PDF source
        docx_path (str): Chemin du fichier Word de destination
    
    Returns:
        bool: True si la conversion est réussie, False sinon
    """
    try:
        # Vérification des chemins
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            logger.error(f"Le fichier PDF {pdf_path} n'existe pas")
            return False

        logger.info(f"Ouverture du fichier PDF: {pdf_path}")
        # Création du document Word
        doc = Document()
        
        # Ouverture du PDF
        with open(pdf_file, 'rb') as file:
            # Création du lecteur PDF
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            logger.info(f"Nombre total de pages: {total_pages}")

            # Traitement de chaque page
            for page_num in range(total_pages):
                logger.info(f"Traitement de la page {page_num + 1}/{total_pages}")
                
                # Extraction du texte de la page
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Ajout d'un saut de page si ce n'est pas la première page
                if page_num > 0:
                    doc.add_page_break()
                
                # Ajout du texte dans le document Word
                doc.add_paragraph(text)
        
        # Sauvegarde du document Word
        logger.info(f"Sauvegarde du document Word: {docx_path}")
        doc.save(docx_path)
        logger.info("Conversion terminée avec succès")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la conversion: {str(e)}")
        return False

# Exemple d'utilisation
if __name__ == "__main__":
    # Chemins des fichiers (à adapter selon vos besoins)
    input_pdf = "chemin/vers/votre/fichier.pdf"
    output_docx = "chemin/vers/votre/fichier.docx"
    
    # Conversion du fichier
    success = convert_pdf_to_docx(input_pdf, output_docx)
    if success:
        print("Conversion réussie !")
    else:
        print("La conversion a échoué.")