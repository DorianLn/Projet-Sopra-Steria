import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ---------------------------
#      HELPERS VISUELS
# ---------------------------

def add_horizontal_line(paragraph):
    """Ajoute une ligne horizontale style Sopra (sous le nom du profil)."""
    p = paragraph._p
    pPr = p.get_or_add_pPr()

    pbdr = OxmlElement('w:pBdr')

    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:color'), '7030A0')  # violet Sopra
    pbdr.append(bottom)

    pPr.append(pbdr)

# ---------------------------
#   CLASSIFICATION COMPÉTENCES
# ---------------------------

TECH_KEYWORDS = [
    "python","java","c++","javascript","typescript","sql","docker","kubernetes",
    "aws","azure","gcp","cloud","devops","ci","cd","ci/cd","git","react","angular",
    "vue","node","node.js","django","flask","github actions","linux"
]

FONC_KEYWORDS = [
    "communication","gestion","travail","team","leadership",
    "organisation","planning","collaboration","management"
]

def classify_competences(lst):
    if not isinstance(lst, list):
        return [], []

    comp_fonct, comp_tech = [], []

    for c in lst:
        if not isinstance(c, str):
            continue
        low = c.lower()

        if any(k in low for k in TECH_KEYWORDS):
            comp_tech.append(c)
        elif any(k in low for k in FONC_KEYWORDS):
            comp_fonct.append(c)
        else:
            comp_tech.append(c)

    return comp_fonct, comp_tech

def bullets(lst):
    if not lst:
        return ""
    return "\n".join(f"• {str(v)}" for v in lst)


def format_experiences(exps):
    if not isinstance(exps, list):
        return ""

    bloc = ""
    for e in exps:
        dates = e.get("dates", "Dates inconnues")
        entreprise = e.get("entreprise", "Entreprise inconnue")
        poste = e.get("poste") or "—"

        bloc += f"{dates} – {entreprise}\n"
        bloc += f"Poste : {poste}\n"
        bloc += "• Tâche principale\n• Tâche secondaire\n\n"

    return bloc.strip()


def format_formations(forms):
    if not isinstance(forms, list):
        return ""
    return "\n".join(
        f"{f.get('etablissement','?')} — {f.get('dates','?')}"
        for f in forms if isinstance(f, dict)
    )


# ---------------------------
#   GENERATE DOCX FINAL
# ---------------------------
def generate_sopra_docx(cv_data, output_path):
    template_path = "templates/sopra_template.docx"

    if not os.path.exists(template_path):
        raise FileNotFoundError(" Template DOCX introuvable")

    doc = Document(template_path)

    contact = cv_data.get("contact", {}) or {}

    # -------------------------
    #  1) GRAND TITRE (Nom)
    # -------------------------
    title_paragraph = doc.paragraphs[0]
    title_paragraph.text = contact.get("nom", "Nom Prénom")

    if title_paragraph.runs:
        title_paragraph.runs[0].bold = True
        title_paragraph.runs[0].font.size = doc.styles['Heading 1'].font.size

    # Ajouter la ligne horizontale style Sopra uniquement sous le titre
    line = doc.add_paragraph()
    add_horizontal_line(line)

    # -------------------------
    # 2) EXTRACTION DES BLOCS
    # -------------------------
    comp_fonct, comp_tech = classify_competences(cv_data.get("competences", []))

    mapping = {
        "{{COMP_FONCT}}": bullets(comp_fonct),
        "{{COMP_TECH}}": bullets(comp_tech),
        "{{EXPERIENCES}}": format_experiences(cv_data.get("experiences")),
        "{{FORMATIONS}}": format_formations(cv_data.get("formations")),
        "{{LANGUES}}": bullets(cv_data.get("langues")),
        "{{CERTIFICATIONS}}": bullets(cv_data.get("certifications")),
        "{{LOISIRS}}": bullets(cv_data.get("loisirs")),
    }

    # -------------------------
    # 3) REMPLACEMENT TEMPLATE
    # -------------------------
    for p in doc.paragraphs:
        for key, val in mapping.items():
            if key in p.text:
                p.text = p.text.replace(key, val)

                # alignement à gauche (dé-justification)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT


    doc.save(output_path)
    return output_path
