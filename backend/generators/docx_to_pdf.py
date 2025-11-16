import pythoncom
from docx2pdf import convert
import time

def convert_docx_to_pdf(input_docx, output_pdf):
    pythoncom.CoInitialize() # Ouvre COM Word (obligatoire sous Windows)

    try:
        convert(input_docx, output_pdf) # Conversion DOCX → PDF
    finally:
        pythoncom.CoUninitialize() # Ferme Word COM
        time.sleep(0.8)   # important : laisse Word se fermer

    return output_pdf
