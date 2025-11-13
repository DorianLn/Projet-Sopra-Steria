from docx2pdf import convert

def convert_docx_to_pdf(input_docx, output_pdf):
    convert(input_docx, output_pdf)
    return output_pdf
