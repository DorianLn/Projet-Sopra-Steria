import re

def extraire_dates(texte):
    """Trouve toutes les dates dans un texte"""
    pattern = r'\b(0[1-9]|[12][0-9]|3[01])[-/](0[1-9]|1[012])[-/](19|20)\d\d\b'
    dates = re.findall(pattern, texte)
    return [f"{d[0]}/{d[1]}/{d[2]}" for d in dates]

def extraire_email(texte):
    """Trouve tous les emails dans un texte"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, texte)

def extraire_telephone(texte):
    """Trouve tous les numéros de téléphone dans un texte"""
    pattern = r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}'
    return re.findall(pattern, texte)