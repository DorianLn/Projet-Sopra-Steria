import re
# test commentaire
def dedupliquer(liste):
    """Élimine les doublons tout en préservant l'ordre d'apparition"""
    return list(dict.fromkeys(liste))

def extraire_dates(texte):
    """Trouve toutes les dates dans un texte avec différents formats"""
    dates = []
    
    # Format JJ/MM/AAAA ou JJ-MM-AAAA
    pattern1 = r'\b(0[1-9]|[12][0-9]|3[01])[-/](0[1-9]|1[012])[-/](19|20)\d\d\b'
    dates_standard = re.findall(pattern1, texte)
    dates.extend([f"{d[0]}/{d[1]}/{d[2]}" for d in dates_standard])
    
    # Format MM/AAAA ou MM-AAAA
    pattern2 = r'\b(0[1-9]|1[012])[-/]((?:19|20)\d{2})\b'
    dates_courtes = re.findall(pattern2, texte)
    dates.extend([f"{d[0]}/{d[1]}" for d in dates_courtes])
    
    # Format Mois AAAA (ex: Mars 2026)
    mois = r"(?:Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Octobre|Novembre|Décembre)"
    pattern3 = f"{mois}\\s+((?:19|20)\\d{{2}})"
    dates_texte = re.findall(pattern3, texte, re.IGNORECASE)
    dates.extend(dates_texte)
    
    # Format AAAA-AAAA (ex: 2024-2025)
    pattern4 = r'((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2})'
    dates_interval = re.findall(pattern4, texte)
    dates.extend([f"{d[0]}-{d[1]}" for d in dates_interval])
    
    return dedupliquer(dates)

def extraire_email(texte):
    """Trouve tous les emails dans un texte"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return dedupliquer(re.findall(pattern, texte))

def extraire_telephone(texte):
    """Trouve tous les numéros de téléphone dans un texte"""
    pattern = r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}'
    return dedupliquer(re.findall(pattern, texte))

def extraire_adresse(texte):
    """Trouve les adresses dans un texte"""
    # Pattern pour différents formats d'adresse
    patterns = [
        # Numéro + rue/avenue/boulevard + code postal + ville
        r'\b(\d+[\s,]+(?:rue|avenue|boulevard|av|bd|place|chemin|impasse)[\s,]+[\w\s]+[\s,]+\d{5}[\s,]+(?!Tel\b)[\w\s-]+?)(?:\s+Tel\b|$)',
        
        # Code postal + ville
        r'\b(\d{5}[\s,]+(?!Tel\b)[\w\s-]+?)(?:\s+Tel\b|$)',
        
        # Ville + département
        r'\b([A-Z][a-zéèêëîïôöûüç]+(?:[-\s][A-Z][a-zéèêëîïôöûüç]+)*[\s,]+\(\d{2,3}\))\b'
    ]
    
    adresses = []
    for pattern in patterns:
        matches = re.finditer(pattern, texte, re.IGNORECASE)
        for match in matches:
            # Nettoie l'adresse (supprime les espaces multiples)
            adresse = re.sub(r'\s+', ' ', match.group(1).strip())
            if adresse not in adresses:
                adresses.append(adresse)
    
    return dedupliquer(adresses)