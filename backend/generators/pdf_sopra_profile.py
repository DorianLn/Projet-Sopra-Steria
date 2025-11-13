from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white

PURPLE = HexColor("#3E206D")
ORANGE = HexColor("#FF5614")
RED    = HexColor("#D1313D")
GREY   = HexColor("#444444")


def split_soft_vs_tech(comps):
    """Sépare compétences fonctionnelles vs techniques (heuristique simple)."""
    if not comps:
        return [], []

    soft_keywords = [
        "communication", "gestion", "leadership", "organisation",
        "autonomie", "équipe", "equipe", "relation", "management"
    ]
    fonctionnelles = []
    techniques = []

    for c in comps:
        low = c.lower()
        if any(k in low for k in soft_keywords):
            fonctionnelles.append(c)
        else:
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


def draw_bullets(c, lines, x, y, max_width=160*mm, line_height=11):
    """
    Affiche une liste à puces simple. Retourne la position Y finale.
    """
    c.setFont("Helvetica", 10)
    c.setFillColor(black)

    for line in lines:
        if not line:
            continue
        # bullet
        c.circle(x, y + 3, 1.5, stroke=1, fill=1)
        # texte
        c.drawString(x + 8, y, line)
        y -= line_height
    return y - 4


def draw_cv_page(cv_data, filename):
    w, h = A4
    left = 25 * mm
    right_margin = 25 * mm
    content_width = w - left - right_margin

    c = canvas.Canvas(filename, pagesize=A4)

    # -------- PAGE 1 --------
    draw_header(
        c,
        title_text=cv_data.get("titre_profil", "Titre du Profil Collaborateur"),
        name=cv_data.get("contact", {}).get("nom", "")
    )

    y = h - 80 * mm  # point de départ contenu

    # --- COMPETENCES FONCTIONNELLES / TECHNIQUES ---
    comps = cv_data.get("competences", []) or []
    comps_fonct, comps_tech = split_soft_vs_tech(comps)

    # Compétences fonctionnelles
    y = draw_section_title(c, "Compétences fonctionnelles", left, y)
    y -= 6
    if comps_fonct:
        y = draw_bullets(c, comps_fonct, left + 4, y)
    else:
        y = draw_bullets(c, ["(non renseigné)"], left + 4, y)

    y -= 10

    # Compétences techniques
    y = draw_section_title(c, "Compétences techniques", left, y)
    y -= 6
    if comps_tech:
        y = draw_bullets(c, comps_tech, left + 4, y)
    else:
        y = draw_bullets(c, ["(non renseigné)"], left + 4, y)

    y -= 14

    # --- EXPERIENCES (on en met 2-3 sur la page 1) ---
    experiences = cv_data.get("experiences", []) or []

    y = draw_section_title(c, "Expériences", left, y)
    y -= 10
    c.setFont("Helvetica", 10)
    c.setFillColor(black)

    for exp in experiences[:2]:
        periode = exp.get("dates", "")
        client = exp.get("entreprise", "")
        fonction = exp.get("poste", "")

        header = f"{periode} - {client} – {fonction}".strip(" -–")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left, y, header)
        y -= 12

        # description / environnement = ici on met les projets liés
        c.setFont("Helvetica-Oblique", 9)
        env = cv_data.get("projets", [])
        if env:
            c.drawString(left + 10, y, "Environnement technique : " + ", ".join(env[:8]))
            y -= 14

        y -= 6

    # --- FORMATION / CERTIF ---
    y = draw_section_title(c, "Formation - Certification", left, y)
    y -= 6

    formations = cv_data.get("formations", []) or []
    certifs = cv_data.get("certifications", []) or []

    lines_form = []
    for f in formations:
        etab = f.get("etablissement", "")
        d = f.get("dates", "")
        if etab or d:
            lines_form.append(f"{etab} ({d})")

    if not lines_form:
        lines_form = ["(non renseigné)"]

    y = draw_bullets(c, lines_form, left + 4, y)

    # certifications
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
    if langues:
        y = draw_bullets(c, langues, left + 4, y)
    else:
        y = draw_bullets(c, ["(non renseigné)"], left + 4, y)

    draw_footer(c, page_num=1)
    c.showPage()

    # -------- PAGE 2 : on peut détailler contact / expériences / projets etc. --------
    draw_header(
        c,
        title_text=cv_data.get("titre_profil", "Titre du Profil Collaborateur"),
        name=cv_data.get("contact", {}).get("nom", "")
    )

    y = h - 80 * mm

    # Section "Résumé & contact détaillé"
    y = draw_section_title(c, "Profil & Contact", left, y)
    y -= 8
    contact = cv_data.get("contact", {})
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    lines_contact = [
        f"Nom : {contact.get('nom', '')}",
        f"Email : {contact.get('email', '')}",
        f"Téléphone : {contact.get('telephone', '')}",
        f"Adresse : {contact.get('adresse', '')}",
    ]
    if cv_data.get("disponibilite"):
        lines_contact.append(f"Disponibilité : {cv_data['disponibilite']}")
    y = draw_bullets(c, lines_contact, left + 4, y)

    y -= 8

    # Expériences détaillées restantes
    if len(experiences) > 2:
        y = draw_section_title(c, "Expériences complémentaires", left, y)
        y -= 10
        for exp in experiences[2:]:
            periode = exp.get("dates", "")
            client = exp.get("entreprise", "")
            fonction = exp.get("poste", "")
            header = f"{periode} - {client} – {fonction}".strip(" -–")
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left, y, header)
            y -= 12
            y -= 8
            if y < 40*mm:
                draw_footer(c, page_num=2)
                c.showPage()
                draw_header(
                    c,
                    title_text=cv_data.get("titre_profil", "Titre du Profil Collaborateur"),
                    name=cv_data.get("contact", {}).get("nom", "")
                )
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
