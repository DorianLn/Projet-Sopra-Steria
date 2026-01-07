from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white

PURPLE = HexColor("#3E206D")
ORANGE = HexColor("#FF5614")
RED    = HexColor("#D1313D")
GREY   = HexColor("#444444")


def split_soft_vs_tech(comps):
    """Sépare compétences fonctionnelles vs techniques avec liste enrichie."""
    if not comps:
        return [], []

    soft_keywords = [
        "communication", "gestion", "leadership", "organisation",
        "autonomie", "équipe", "equipe", "relation", "management",
        "négociation", "collaboration", "travail", "team", "planning",
        "résolution", "problèmes", "analyse", "client", "présentation"
    ]
    
    tech_keywords = [
        "python", "java", "javascript", "typescript", "c++", "c#", "sql",
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux",
        "react", "angular", "vue", "node", "django", "flask", "api",
        "devops", "ci/cd", "cloud", "mongodb", "postgresql", "html", "css"
    ]
    
    fonctionnelles = []
    techniques = []
    seen_fonct, seen_tech = set(), set()

    for c in comps:
        if not c or not isinstance(c, str):
            continue
        low = c.lower().strip()
        
        if any(k in low for k in soft_keywords):
            if low not in seen_fonct:
                seen_fonct.add(low)
                fonctionnelles.append(c)
        elif any(k in low for k in tech_keywords):
            if low not in seen_tech:
                seen_tech.add(low)
                techniques.append(c)
        else:
            if low not in seen_tech:
                seen_tech.add(low)
                techniques.append(c)

    return fonctionnelles, techniques


def draw_header(c, title_text, name):
    w, h = A4
    left = 25 * mm
    top = h - 35 * mm

    # Petit "CURRICULUM VITAE"
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(RED)
    c.drawString(left, top + 20, "CURRICULUM VITAE")

    # Gros titre
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(left, top, title_text)

    # Nom sous le titre (optionnel)
    if name:
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(GREY)
        c.drawString(left, top - 24, name)

    # Ligne horizontale dégradée (approx : deux rectangles)
    y_line = top - 34
    c.setFillColor(PURPLE)
    c.rect(left, y_line, 90 * mm, 1.5, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.rect(left + 90 * mm, y_line, 60 * mm, 1.5, stroke=0, fill=1)


def draw_footer(c, page_num):
    w, h = A4
    # Bande dégradée en bas
    c.setFillColor(PURPLE)
    c.rect(0, 8*mm, w/2, 4, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.rect(w/2, 8*mm, w/2, 4, stroke=0, fill=1)

    # Logo / texte Sopra Steria (placeholder texte)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(PURPLE)
    c.drawRightString(w - 25*mm, 16*mm, "sopra")
    c.setFillColor(ORANGE)
    c.drawString(w - 25*mm, 16*mm, " steria")

    # Numéro de page
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY)
    c.drawString(25*mm, 16*mm, f"{page_num}/2")  # tu peux rendre ça dynamique


def draw_section_title(c, text, x, y):
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, text)
    return y - 8


def draw_bullets(c, lines, x, y, max_width=160*mm, line_height=11, fallback_text=None):
    """
    Affiche une liste à puces simple. Retourne la position Y finale.
    Gère le texte long et fournit un fallback si la liste est vide.
    """
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    if not lines or not any(lines):
        if fallback_text:
            c.drawString(x + 8, y, fallback_text)
            return y - line_height
        return y

    for line in lines:
        if not line:
            continue
        
        line_str = str(line).strip()
        if not line_str:
            continue
        
        if len(line_str) > 80:
            line_str = line_str[:77] + "..."
        
        c.circle(x, y + 3, 1.5, stroke=1, fill=1)
        c.drawString(x + 8, y, line_str)
        y -= line_height
        
        if y < 30 * mm:
            break
            
    return y - 4


def draw_cv_page(cv_data, filename):
    w, h = A4
    left = 25 * mm
    right_margin = 25 * mm
    content_width = w - left - right_margin

    c = canvas.Canvas(filename, pagesize=A4)
    
    # Récupération sécurisée des données
    contact = cv_data.get("contact", {}) or {}
    nom = contact.get("nom") or "Nom non renseigné"
    titre_profil = cv_data.get("titre_profil") or "Profil Collaborateur"

    # -------- PAGE 1 --------
    draw_header(c, title_text=titre_profil, name=nom)

    y = h - 80 * mm

    # --- COMPETENCES FONCTIONNELLES / TECHNIQUES ---
    comps = cv_data.get("competences", []) or []
    comps_fonct, comps_tech = split_soft_vs_tech(comps)

    y = draw_section_title(c, "Compétences fonctionnelles", left, y)
    y -= 6
    y = draw_bullets(c, comps_fonct, left + 4, y, fallback_text="Non renseigné")

    y -= 10

    y = draw_section_title(c, "Compétences techniques", left, y)
    y -= 6
    y = draw_bullets(c, comps_tech, left + 4, y, fallback_text="Non renseigné")

    y -= 14

    # --- EXPERIENCES ---
    experiences = cv_data.get("experiences", []) or []

    y = draw_section_title(c, "Expériences", left, y)
    y -= 10
    c.setFont("Helvetica", 10)
    c.setFillColor(black)

    if experiences:
        for exp in experiences[:3]:
            if not isinstance(exp, dict):
                continue
            periode = exp.get("dates") or "Dates non précisées"
            client = exp.get("entreprise") or "Entreprise non précisée"
            fonction = exp.get("poste") or "Poste non précisé"
            description = exp.get("description")

            header = f"{periode} - {client}"
            if fonction and fonction != "Poste non précisé":
                header += f" – {fonction}"
            
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left, y, header[:80])
            y -= 12

            if description and description.strip():
                c.setFont("Helvetica", 9)
                desc_text = description.strip()[:100]
                c.drawString(left + 10, y, f"• {desc_text}")
                y -= 12

            y -= 6
            
            if y < 60 * mm:
                break
    else:
        c.setFont("Helvetica", 10)
        c.drawString(left + 10, y, "Aucune expérience renseignée")
        y -= 12

    # --- FORMATION / CERTIF ---
    y = draw_section_title(c, "Formation - Certification", left, y)
    y -= 6

    formations = cv_data.get("formations", []) or []
    certifs = cv_data.get("certifications", []) or []

    lines_form = []
    for f in formations:
        if not isinstance(f, dict):
            continue
        etab = f.get("etablissement") or ""
        d = f.get("dates") or ""
        diplome = f.get("diplome")
        
        if diplome:
            lines_form.append(f"{diplome} – {etab} ({d})")
        elif etab:
            lines_form.append(f"{etab} ({d})")

    y = draw_bullets(c, lines_form, left + 4, y, fallback_text="Non renseigné")

    if certifs:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left + 4, y, "Certifications :")
        y -= 12
        y = draw_bullets(c, certifs, left + 8, y)

    y -= 10

    # --- Langues ---
    y = draw_section_title(c, "Langue(s)", left, y)
    y -= 6
    langues = cv_data.get("langues", []) or []
    y = draw_bullets(c, langues, left + 4, y, fallback_text="Non renseigné")

    draw_footer(c, page_num=1)
    c.showPage()

    # -------- PAGE 2 : Contact / Expériences complémentaires / Projets --------
    draw_header(c, title_text=titre_profil, name=nom)

    y = h - 80 * mm

    # Section "Profil & Contact"
    y = draw_section_title(c, "Profil & Contact", left, y)
    y -= 8
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    lines_contact = []
    if contact.get('nom'):
        lines_contact.append(f"Nom : {contact['nom']}")
    if contact.get('email'):
        lines_contact.append(f"Email : {contact['email']}")
    if contact.get('telephone'):
        lines_contact.append(f"Téléphone : {contact['telephone']}")
    if contact.get('adresse'):
        lines_contact.append(f"Adresse : {contact['adresse']}")
    if cv_data.get("disponibilite"):
        lines_contact.append(f"Disponibilité : {cv_data['disponibilite']}")
    
    y = draw_bullets(c, lines_contact, left + 4, y, fallback_text="Contact non renseigné")

    y -= 8

    # Expériences complémentaires (si plus de 3)
    if len(experiences) > 3:
        y = draw_section_title(c, "Expériences complémentaires", left, y)
        y -= 10
        for exp in experiences[3:]:
            if not isinstance(exp, dict):
                continue
            periode = exp.get("dates") or ""
            client = exp.get("entreprise") or ""
            fonction = exp.get("poste") or ""
            
            header = f"{periode} - {client}"
            if fonction:
                header += f" – {fonction}"
            header = header.strip(" -–")[:80]
            
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left, y, header)
            y -= 12
            y -= 8
            
            if y < 40*mm:
                draw_footer(c, page_num=2)
                c.showPage()
                draw_header(c, title_text=titre_profil, name=nom)
                y = h - 80*mm

    # Projets / Loisirs
    y -= 4
    if cv_data.get("projets"):
        y = draw_section_title(c, "Projets clés", left, y)
        y -= 6
        y = draw_bullets(c, cv_data["projets"], left + 4, y)

    y -= 6
    if cv_data.get("loisirs"):
        y = draw_section_title(c, "Centres d’intérêt / Loisirs", left, y)
        y -= 6
        y = draw_bullets(c, cv_data["loisirs"], left + 4, y)

    draw_footer(c, page_num=2)
    c.save()


def generate_sopra_profile_pdf(cv_data, output_path):
    """
    Fonction principale à appeler depuis ton backend.
    cv_data = JSON structuré issu de l'extraction.
    output_path = chemin du PDF à générer.
    """
    draw_cv_page(cv_data, output_path)
