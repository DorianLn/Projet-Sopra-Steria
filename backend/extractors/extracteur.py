# backend/extractors/extracteur.py
import re

def dedupliquer(liste):
    """Élimine les doublons tout en préservant l'ordre d'apparition"""
    return list(dict.fromkeys(liste))

def extraire_nom_prenom(texte):
    """Extrait le nom et prénom (généralement en début du CV)"""
    lignes = texte.strip().split('\n')
    
    # Filtrer les lignes vides
    lignes = [l.strip() for l in lignes if l.strip()]
    
    # D'abord, extraire toutes les adresses pour vérification croisée
    texte_lower = texte.lower()
    
    # Patterns à rejeter absolument
    patterns_rejet = [
        r'rue\s+[A-Z][a-zéèêëîïôöûüçÀ-ÿ]+\s+[A-Z][a-zéèêëîïôöûüçÀ-ÿ]+',  # "rue Pierre Bourdan"
        r'(?:rue|avenue|boulevard|place|chemin|impasse|allée|allee|cour|quai|avenue|passage|square|boulevard)\s+',  # Commence par mot d'adresse
        r'\d{1,4}\s*[,\s]+(?:rue|avenue|boulevard|place|chemin|impasse|allée|allee)',  # Adresse avec numéro
        r'rue|avenue|boulevard|place|chemin|impasse|allée|allee',  # Mot d'adresse
        r'\d{5}(?:\s|$)',  # Code postal
        r'Téléphone|Phone|Tel|tél|T\.',  # Téléphone
        r'@',  # Email
        r'Adresse',  # Adresse
        r'Nom',  # Label Nom
        r'(?:FORMATION|Études?|CURSUS|Scolarité|EXPÉRIENCE|Experience|PARCOURS|COMPÉTENCE|Competence|LOISIR|Intérêt|LANGUES)',  # Sections CV
        r'(?:Responsable|Développeur|Ingénieur|Manager|Chef|Consultant|Lead|Analyst|Admin|Architecte|Directeur)',  # Mots de postes
        r'(?:Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Octobre|Novembre|Décembre)',  # Mois
        r'20\d{2}|19\d{2}',  # Années
    ]
    
    # Trouver les noms qui apparaissent dans une adresse (à exclure)
    noms_dans_adresse = set()
    pattern_rue_nom = r'(?:rue|avenue|boulevard|place|chemin|impasse|allée)\s+([A-Za-zéèêëîïôöûüçÀ-ÿ]+\s+[A-Za-zéèêëîïôöûüçÀ-ÿ]+)'
    for match in re.finditer(pattern_rue_nom, texte, re.IGNORECASE):
        nom_rue = match.group(1).strip().lower()
        noms_dans_adresse.add(nom_rue)
    
    for ligne in lignes[:5]:  # Chercher dans les 5 premières lignes
        # Rejeter si contient un pattern suspect
        rejet = False
        for pattern in patterns_rejet:
            if re.search(pattern, ligne, re.IGNORECASE):
                rejet = True
                break
        
        if rejet:
            continue
        
        # Passer les lignes trop courtes ou trop longues
        if len(ligne) < 5 or len(ligne) > 60:
            continue
        
        # Nettoyer la ligne (retirer chiffres et caractères spéciaux SAUF tirets)
        nom_prenom = re.sub(r'[0-9\(\)\.,;:│]', '', ligne).strip()
        nom_prenom = re.sub(r'\s+', ' ', nom_prenom)  # Normaliser les espaces
        
        # Vérifier que c'est un vrai nom
        mots = nom_prenom.split()
        
        # Un nom/prénom valide :
        # - 2-3 mots maximum (Nom Prénom ou Prénom Nom ou Prénom Deuxième-Nom)
        # - Chaque mot entre 2 et 25 caractères
        # - Commence par une majuscule
        if len(mots) >= 2 and len(mots) <= 3:
            # Vérifier la longueur de chaque mot (accepter tirets)
            if all(2 <= len(mot.replace('-', '')) <= 25 for mot in mots):
                # Vérifier que chaque mot commence par une majuscule (ou un caractère accentué majuscule)
                if all(mot[0].isupper() or mot[0] in 'ÀÂÄÆÉÈÊËÏÎÔŒÙÛÜŒÇÑ' for mot in mots):
                    # Rejeter les lignes qui contiendraient des nombres cachés
                    if not re.search(r'\d', ligne):
                        nom_candidat = ' '.join(mots)
                        
                        # VÉRIFICATION CROISÉE : rejeter si ce nom apparaît dans une adresse
                        if nom_candidat.lower() not in noms_dans_adresse:
                            return nom_candidat
    
    # Si pas de nom trouvé, essayer d'extraire depuis l'email
    email_match = re.search(r'([a-zA-Z]+)[._]([a-zA-Z]+)@', texte)
    if email_match:
        prenom = email_match.group(1).capitalize()
        nom = email_match.group(2).capitalize()
        if len(prenom) > 1 and len(nom) > 1:
            return f"{prenom} {nom}"
    
    return None

def extraire_formations(texte):
    """Extrait les formations (diplômes, écoles, certifications)"""
    formations = []
    
    # Trouver la section FORMATION
    pattern_section = r'(?:FORMATION|Études?|CURSUS|Scolarité)[\s\n:=]*(.*?)(?=\n(?:EXPÉRIENCE|Experience|COMPÉTENCE|Competence|LOISIR|Intérêt|LANGUES|SKILLS|$))'
    match_section = re.search(pattern_section, texte, re.IGNORECASE | re.DOTALL)
    
    if match_section:
        section_formation = match_section.group(1)
    else:
        # Si pas de section claire, utiliser tout le texte
        section_formation = texte
    
    # Patterns pour extraire les formations
    patterns = [
        r"((?:Master|Licence|Bac\+[0-9]|Bac|Diplôme|Diplome|Bachelor|BTS|DUT|DEUST|Certificat|Certification)(?:\s+(?:en|d'|de|du|des))?\s+[A-Za-zéèêëîïôöûüçÀ-ÿ\s\-\']+?)(?:\s*[-–—]|\n|\s*[-–—]\s*|[\(\[])",
        r"((?:Université|Ecole|École|Institut|Institiut|Académie)\s+[A-Za-zéèêëîïôöûüçÀ-ÿ\s\-\'\.]+?)(?:\s*[-–—]|\n|[\(\[]|$)",
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, section_formation, re.IGNORECASE):
            formation = match.group(1).strip()
            formation = re.sub(r'\s+', ' ', formation)
            formation = re.sub(r'[\(\[].*?[\)\]]', '', formation).strip()
            
            # Filtrer les entrées invalides
            if len(formation) > 5 and len(formation) < 100 and formation not in formations:
                # Rejeter si contient des mots d'expérience
                if not re.search(r'(?:Développeur|Ingénieur|Manager|Chef|Consultant|Responsable|Lead|Analyst|Admin|Architecte|Poste|Titre)\b', formation, re.IGNORECASE):
                    if not re.search(r'^\d+|Téléphone|Email|rue|avenue', formation, re.IGNORECASE):
                        formations.append(formation)
    
    return dedupliquer(formations)

def extraire_experiences(texte):
    """Extrait les expériences professionnelles"""
    experiences = []
    
    # Trouver la section EXPÉRIENCE
    pattern_section = r'(?:EXPÉRIENCE|Experience|PARCOURS|HISTORIQUE|Expériences)[\s\n:=]*(.*?)(?=\n(?:FORMATION|COMPÉTENCE|Competence|LOISIR|Intérêt|LANGUES|$))'
    match_section = re.search(pattern_section, texte, re.IGNORECASE | re.DOTALL)
    
    if match_section:
        section_exp = match_section.group(1)
    else:
        section_exp = texte
    
    # Mots clés pour identifier les postes
    postes_keywords = r'(?:Développeur|Ingénieur|Manager|Chef|Consultant|Responsable|Lead|Analyst|Admin|Architecte|Directeur|Coordinateur|Spécialiste|Agent|Technicien|Employé)'
    
    # Chercher: "Poste - Entreprise" sur la MÊME LIGNE
    pattern = rf'({postes_keywords}[A-Za-zéèêëîïôöûüçÀ-ÿ\s\-\']*?)\s*[-–—]\s*([A-Za-zéèêëîïôöûüçÀ-ÿ0-9\s\-\'\.]+?)$'
    
    for line in section_exp.split('\n'):
        line = line.strip()
        if not line or len(line) < 10:
            continue
            
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            poste = match.group(1).strip()
            entreprise = match.group(2).strip()
            
            experience = f"{poste} - {entreprise}"
            experience = re.sub(r'\s+', ' ', experience)
            
            # Filtrer
            if len(experience) > 10 and len(experience) < 150 and experience not in experiences:
                # Rejeter si contient des mots de formation
                if not re.search(r'Master|Licence|Bac|Diplôme|Ecole|Université|BTS|DUT', experience, re.IGNORECASE):
                    experiences.append(experience)
    
    return dedupliquer(experiences)


def extraire_loisirs(texte):
    """Extrait les loisirs et centres d'intérêt"""
    loisirs = []
    
    sections = re.split(r'(?:Loisir|Intérêt|Centre d[\'e] intérêt|Passion|Hobby|Activité|Activites|Sports?|Divers)[\s,]*[:\-]?', texte, flags=re.IGNORECASE)
    
    if len(sections) > 1:
        section_loisirs = sections[-1]
        section_loisirs = re.split(r'(?:Référence|Contact|Signature|Disponibilité)', section_loisirs, flags=re.IGNORECASE)[0]
        
        items = re.split(r'[,;•\-\n]', section_loisirs)
        for item in items:
            item = item.strip()
            if len(item) > 2 and len(item) < 100:
                if not re.search(r'^\d+|email|@|\d{5}', item, re.IGNORECASE):
                    if not re.search(r'^(?:et|ou|de|d[\'e]|à|en)\s', item, re.IGNORECASE):
                        loisirs.append(item)
    
    return dedupliquer(loisirs)

def extraire_dates(texte):
    """Trouve toutes les dates dans un texte avec différents formats"""
    dates = []
    
    # Format AAAA-AAAA / AAAA–AAAA (plages d'années) - priorité haute
    pattern_plage = r'((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|[Pp]résent|[Aa]ctuel(?:lement)?|[Aa]ujourd)'
    for m in re.finditer(pattern_plage, texte):
        debut, fin = m.group(1), m.group(2)
        if fin.lower() in ('présent', 'present', 'actuel', 'actuellement', 'aujourd'):
            dates.append(f"{debut} - Présent")
        else:
            dates.append(f"{debut}-{fin}")
    
    # Format Mois AAAA - Mois AAAA ou Mois AAAA - Présent
    mois = r"(?:Janvier|Février|Fevrier|Mars|Avril|Mai|Juin|Juillet|Août|Aout|Septembre|Octobre|Novembre|Décembre|Decembre)"
    pattern_mois_plage = rf"({mois})\s*(\d{{4}})\s*[-–—]\s*(?:({mois})\s*(\d{{4}})|([Pp]résent|[Aa]ctuel(?:lement)?))"
    for m in re.finditer(pattern_mois_plage, texte, re.IGNORECASE):
        mois_deb, annee_deb = m.group(1), m.group(2)
        if m.group(5):
            dates.append(f"{mois_deb} {annee_deb} - Présent")
        elif m.group(3) and m.group(4):
            dates.append(f"{mois_deb} {annee_deb} - {m.group(3)} {m.group(4)}")
    
    # Format Mois AAAA seul (ex: Mars 2026)
    pattern_mois_seul = rf"\b({mois})\s+((?:19|20)\d{{2}})\b"
    for m in re.finditer(pattern_mois_seul, texte, re.IGNORECASE):
        date_str = f"{m.group(1)} {m.group(2)}"
        if date_str not in dates and not any(date_str in d for d in dates):
            dates.append(date_str)
    
    # Format JJ/MM/AAAA ou JJ-MM-AAAA
    pattern_jma = r'\b(0?[1-9]|[12][0-9]|3[01])[-/](0?[1-9]|1[012])[-/]((?:19|20)\d{2})\b'
    for m in re.finditer(pattern_jma, texte):
        start_pos = m.start()
        if not re.search(r'\d{5}', texte[max(0,start_pos-10):start_pos+15]):
            dates.append(f"{m.group(1).zfill(2)}/{m.group(2).zfill(2)}/{m.group(3)}")
    
    # Format MM/AAAA ou MM-AAAA (éviter confusion avec codes postaux)
    pattern_ma = r'\b(0?[1-9]|1[012])[-/]((?:19|20)\d{2})\b'
    for m in re.finditer(pattern_ma, texte):
        start_pos = m.start()
        window = texte[max(0,start_pos-15):start_pos+20]
        if not re.search(r'\d{5}', window):
            date_str = f"{m.group(1).zfill(2)}/{m.group(2)}"
            if date_str not in dates:
                dates.append(date_str)
    
    # Années seules (contexte CV : éviter codes postaux)
    pattern_annee = r'(?<!\d)(?<!/)(?<![/-])((?:19|20)\d{2})(?!\d)(?!/|-)'
    for m in re.finditer(pattern_annee, texte):
        annee = m.group(1)
        start_pos = m.start()
        window = texte[max(0,start_pos-20):start_pos+25]
        if not re.search(r'\d{5}', window) and annee not in dates:
            if not any(annee in d for d in dates):
                dates.append(annee)
    
    return dedupliquer(dates)

def extraire_email(texte):
    """Trouve tous les emails dans un texte avec nettoyage"""
    pattern = r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}'
    emails = []
    for m in re.finditer(pattern, texte):
        email = m.group(0).strip().lower()
        email = re.sub(r'^[.\-_]+|[.\-_]+$', '', email)
        if email and '@' in email and '.' in email.split('@')[1]:
            emails.append(email)
    return dedupliquer(emails)

def extraire_telephone(texte):
    """Trouve tous les numéros de téléphone dans un texte avec normalisation"""
    patterns = [
        r'(?:\+33|0033|0)\s*[1-9](?:[\s.\-]*\d{2}){4}',
        r'\+?\d{1,3}[\s.\-]?\(?\d{1,4}\)?[\s.\-]?\d{2,4}[\s.\-]?\d{2,4}[\s.\-]?\d{2,4}',
    ]
    telephones = []
    for pattern in patterns:
        for m in re.finditer(pattern, texte):
            tel = m.group(0).strip()
            tel_clean = re.sub(r'[\s.\-()]', '', tel)
            if len(tel_clean) >= 10 and len(tel_clean) <= 15:
                tel_format = re.sub(r'[\s.\-]+', ' ', tel).strip()
                if tel_format not in telephones:
                    telephones.append(tel_format)
    return dedupliquer(telephones)

def extraire_adresse(texte):
    """Trouve les adresses dans un texte avec patterns améliorés"""
    patterns = [
        r'\b(\d{1,4}[,\s]+(?:rue|avenue|boulevard|av\.?|bd\.?|place|chemin|impasse|allée|allee|passage|quai|route)[\s,]+[A-Za-zéèêëîïôöûüçÀ-ÿ\s\-\']+[,\s]+\d{5}[\s,]+[A-Za-zéèêëîïôöûüçÀ-ÿ\s\-\']+)',
        r'\b(\d{1,4}[,\s]+(?:rue|avenue|boulevard|av\.?|bd\.?|place|chemin|impasse|allée|allee)[\s,]+[A-Za-zéèêëîïôöûüçÀ-ÿ\s\-\']{3,50})(?=[\s\n,]|$)',
        r'\b(\d{5})[\s,]+([A-Za-zéèêëîïôöûüçÀ-ÿ][A-Za-zéèêëîïôöûüçÀ-ÿ\s\-\']{2,30})(?=[\s,\n]|$)',
    ]
    
    adresses = []
    for i, pattern in enumerate(patterns):
        for match in re.finditer(pattern, texte, re.IGNORECASE):
            if i == 2:
                adresse = f"{match.group(1)} {match.group(2)}"
            else:
                adresse = match.group(1)
            
            adresse = re.sub(r'\s+', ' ', adresse.strip())
            adresse = re.sub(r'[\s]+$', '', adresse)
            adresse = re.sub(r'(?:Téléphone|Email|Tel|tél).*$', '', adresse).strip()
            
            if len(adresse) > 5 and adresse not in adresses:
                if not re.search(r'\b(?:Tel|Email|@|www\.)\b', adresse, re.IGNORECASE):
                    adresses.append(adresse)
    
    return dedupliquer(adresses)