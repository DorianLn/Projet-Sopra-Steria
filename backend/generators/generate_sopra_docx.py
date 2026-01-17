import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor
from typing import Dict, List, Optional, Any
import re

# ---------------------------
#      HELPERS VISUELS
# ---------------------------

def add_horizontal_line(paragraph, color="7030A0"):
    """Ajoute une ligne horizontale style Sopra (sous le nom du profil)."""
    p = paragraph._p
    pPr = p.get_or_add_pPr()

    pbdr = OxmlElement('w:pBdr')

    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:color'), color)  # violet Sopra par défaut
    pbdr.append(bottom)

    pPr.append(pbdr)


def set_cell_shading(cell, color):
    """Définit la couleur de fond d'une cellule."""
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading_elm)

# ---------------------------
#   CLASSIFICATION COMPÉTENCES
# ---------------------------

TECH_KEYWORDS = [
    "python","java","c++","c#","javascript","typescript","sql","docker","kubernetes",
    "aws","azure","gcp","cloud","devops","ci","cd","ci/cd","git","react","angular",
    "vue","node","node.js","django","flask","fastapi","spring","github","gitlab",
    "linux","mongodb","postgresql","mysql","redis","kafka","api","rest","graphql",
    ".net","php","ruby","go","rust","swift","kotlin","scala","html","css","sass"
]

FONC_KEYWORDS = [
    "communication","gestion","travail","team","leadership","équipe","equipe",
    "organisation","planning","collaboration","management","autonomie","analyse",
    "résolution","problèmes","relation","client","négociation","presentation"
]

def classify_competences(lst):
    if not isinstance(lst, list):
        return [], []

    comp_fonct, comp_tech = [], []
    seen_fonct, seen_tech = set(), set()

    for c in lst:
        if not isinstance(c, str):
            continue
        low = c.lower().strip()
        
        if not low or len(low) < 2:
            continue

        if any(k in low for k in TECH_KEYWORDS):
            if low not in seen_tech:
                seen_tech.add(low)
                comp_tech.append(c)
        elif any(k in low for k in FONC_KEYWORDS):
            if low not in seen_fonct:
                seen_fonct.add(low)
                comp_fonct.append(c)
        else:
            if low not in seen_tech:
                seen_tech.add(low)
                comp_tech.append(c)

    return comp_fonct, comp_tech

def bullets(lst, fallback="Non renseigné"):
    """Génère une liste à puces avec fallback intelligent"""
    if not lst:
        return f"• {fallback}"
    clean_items = [str(v).strip() for v in lst if v and str(v).strip()]
    if not clean_items:
        return f"• {fallback}"
    return "\n".join(f"• {v}" for v in clean_items)



def format_experiences(exps: List[Dict], style: str = "professional") -> str:
    """
    Formate les expériences avec les données réelles extraites.
    
    Args:
        exps: Liste des expériences structurées
        style: "professional" (détaillé) ou "compact" (résumé)
    """
    if not isinstance(exps, list) or not exps:
        return "• Aucune expérience renseignée"

    bloc = ""
    
    # Trier par date (anti-chronologique)
    sorted_exps = sort_experiences_by_date(exps)
    
    for e in sorted_exps:
        if not isinstance(e, dict):
            continue
        
        # Extraire les données
        dates = normalize_date_display(e.get("dates"))
        entreprise = e.get("entreprise") or "Entreprise non précisée"
        poste = e.get("poste") or ""
        lieu = e.get("lieu", "")
        description = e.get("description")

        if style == "professional":
            # Format professionnel détaillé
            header = f"{dates}"
            if lieu:
                header += f" – {lieu}"
            bloc += f"{header}\n"
            
            if poste:
                bloc += f"**{poste}** – {entreprise}\n"
            else:
                bloc += f"**{entreprise}**\n"
            
            if description and description.strip():
                # Formater la description avec des puces
                desc_lines = description.strip().split('\n')
                for line in desc_lines:
                    line = line.strip()
                    if line and not line.startswith('•') and not line.startswith('-'):
                        bloc += f"  • {line}\n"
                    elif line:
                        bloc += f"  {line}\n"
            
            bloc += "\n"
        else:
            # Format compact
            if poste:
                bloc += f"• {poste} – {entreprise} ({dates})\n"
            else:
                bloc += f"• {entreprise} ({dates})\n"

    return bloc.strip() if bloc.strip() else "• Aucune expérience renseignée"


def format_formations(forms: List[Dict], style: str = "professional") -> str:
    """
    Formate les formations avec diplôme si disponible.
    
    Args:
        forms: Liste des formations structurées
        style: "professional" (détaillé) ou "compact" (résumé)
    """
    if not isinstance(forms, list) or not forms:
        return "• Aucune formation renseignée"
    
    # Trier par date (anti-chronologique)
    sorted_forms = sort_formations_by_date(forms)
    
    lines = []
    for f in sorted_forms:
        if not isinstance(f, dict):
            continue
        
        etablissement = f.get('etablissement', 'Établissement non précisé')
        dates = normalize_date_display(f.get('dates'))
        diplome = f.get('diplome')
        lieu = f.get('lieu', '')
        
        if style == "professional":
            if diplome:
                line = f"**{diplome}**\n  {etablissement}"
                if lieu:
                    line += f" – {lieu}"
                line += f" ({dates})"
            else:
                line = f"**{etablissement}**"
                if lieu:
                    line += f" – {lieu}"
                line += f" ({dates})"
            lines.append(line)
        else:
            # Format compact
            if diplome:
                lines.append(f"• {diplome} – {etablissement} ({dates})")
            else:
                lines.append(f"• {etablissement} ({dates})")
    
    return "\n".join(lines) if lines else "• Aucune formation renseignée"


def build_experience_slots(experiences: List[Dict], max_slots: int = 3) -> Dict[str, str]:
    slots = {}
    exps_sorted = sort_experiences_by_date(experiences)[:max_slots]

    for i in range(1, max_slots + 1):
        if i <= len(exps_sorted):
            e = exps_sorted[i - 1]
            slots[f"{{{{PERIODE_{i}}}}}"] = normalize_date_display(e.get("dates"))
            slots[f"{{{{CLIENT_{i}}}}}"] = (e.get("entreprise") or "").strip()
            slots[f"{{{{INTITULE_MISSION_{i}}}}}"] = (e.get("mission") or e.get("intitule") or "").strip()
            slots[f"{{{{FONCTION_{i}}}}}"] = (e.get("poste") or "").strip()
            slots[f"{{{{DESCRIPTION_MISSION_{i}}}}}"] = (e.get("description") or "").strip()
            slots[f"{{{{ENV_TECH_{i}}}}}"] = (e.get("environnement_technique") or "").strip()
        else:
            for k in ["PERIODE", "CLIENT", "INTITULE_MISSION", "FONCTION", "DESCRIPTION_MISSION", "ENV_TECH"]:
                slots[f"{{{{{k}_{i}}}}}"] = ""

    return slots

def cleanup_empty_experience_blocks(doc):
    to_delete = []

    for p in doc.paragraphs:
        text = p.text.strip()

        # Ligne d'expérience vide : " -  -  - " ou variations
        if re.fullmatch(r'[-\s–—]*', text):
            to_delete.append(p)

        # Environnement technique vide
        if text.lower().startswith("environnement technique") and ":" in text and len(text.split(":")[-1].strip()) == 0:
            to_delete.append(p)

    for p in to_delete:
        p._element.getparent().remove(p._element)


def sort_experiences_by_date(exps: List[Dict]) -> List[Dict]:
    """Trie les expériences par date (anti-chronologique)."""
    def extract_year(exp):
        dates = str(exp.get("dates", ""))
        match = re.search(r'(19|20)\d{2}', dates)
        return int(match.group(0)) if match else 0
    
    return sorted(exps, key=extract_year, reverse=True)


def sort_formations_by_date(forms: List[Dict]) -> List[Dict]:
    """Trie les formations par date (anti-chronologique)."""
    def extract_year(form):
        dates = str(form.get("dates", ""))
        match = re.search(r'(19|20)\d{2}', dates)
        return int(match.group(0)) if match else 0
    
    return sorted(forms, key=extract_year, reverse=True)


def normalize_date_display(date_str: Optional[str]) -> str:
    """Normalise l'affichage des dates."""
    if not date_str:
        return "Dates non précisées"
    
    date_str = str(date_str).strip()
    
    # Normaliser les tirets
    date_str = re.sub(r'\s*[-–—]\s*', ' – ', date_str)
    
    # Normaliser "Présent"
    date_str = re.sub(r'(?i)\b(actuel|actuellement|aujourd\'?hui)\b', 'Présent', date_str)
    
    return date_str


def format_contact(contact):
    """Formate les informations de contact"""
    if not isinstance(contact, dict):
        return ""
    
    lines = []
    if contact.get("email"):
        lines.append(f"Email : {contact['email']}")
    if contact.get("telephone"):
        lines.append(f"Tél : {contact['telephone']}")
    if contact.get("adresse"):
        lines.append(f"Adresse : {contact['adresse']}")
    
    return "\n".join(lines) if lines else "Contact non renseigné"

def replace_variables_in_docx(doc, mapping: Dict[str, str]):
    def replace_in_paragraph(paragraph):
        for run in paragraph.runs:
            for key, val in mapping.items():
                if key in run.text:
                    run.text = run.text.replace(key, val or "")

    for p in doc.paragraphs:
        replace_in_paragraph(p)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    replace_in_paragraph(p)

    for section in doc.sections:
        for p in section.header.paragraphs:
            replace_in_paragraph(p)
        for p in section.footer.paragraphs:
            replace_in_paragraph(p)


# ---------------------------
#   GENERATE DOCX FINAL
# ---------------------------
def generate_sopra_docx(cv_data, output_path):
    template_path = "templates/sopra_template.docx"

    if not os.path.exists(template_path):
        raise FileNotFoundError("Template DOCX introuvable")

    doc = Document(template_path)

    contact = cv_data.get("contact", {}) or {}
    titre_profil = cv_data.get("titre_profil") or "Profil Collaborateur"
    nom = contact.get("nom") or "Nom Prénom"

    competences = cv_data.get("competences", {})

    comp_tech_text = format_competences_techniques(
        competences.get("techniques", {})
    )

    comp_fonct_text = format_competences_fonctionnelles(
        competences.get("fonctionnelles", [])
    )
    experience_slots = build_experience_slots(cv_data.get("experiences", []))

    # Préparer formations + certifications
    certifs = bullets(cv_data.get("certifications", []), "").strip()
    form_cert = format_formations(cv_data.get("formations"))
    if certifs:
        form_cert += "\n" + certifs

    mapping = {
        "{{TITRE_PROFIL}}": titre_profil,
        "{{NOM_PRENOM}}": nom,
        "{{COMP_FONCT}}": comp_fonct_text,
        "{{COMP_TECH}}": comp_tech_text,
        "{{FORMATIONS_CERTIFICATIONS}}": form_cert,
        "{{LANGUES}}": bullets(cv_data.get("langues", [])),
    }

    mapping.update(experience_slots)

    replace_variables_in_docx(doc, mapping)
    cleanup_empty_experience_blocks(doc)

    doc.save(output_path)
    return output_path

def format_competences_techniques(tech_dict):
    """
    Transforme la structure :
    {
      "programmation": [...],
      "frameworks": [...],
      "bases_de_donnees": [...],
      "outils": [...]
    }
    en texte structuré pour DOCX
    """

    if not isinstance(tech_dict, dict):
        return "• Aucune compétence technique"

    result = []

    mapping_titres = {
        "programmation": "Programmation",
        "frameworks": "Frameworks",
        "bases_de_donnees": "Bases de données",
        "devops_cloud": "DevOps & Cloud",
        "outils": "Outils",
        "autres": "Autres compétences"
    }

    for key, values in tech_dict.items():
        if not values:
            continue

        titre = mapping_titres.get(key, key.capitalize())

        result.append(f"{titre} :")

        clean_values = [str(v).strip() for v in values if v and str(v).strip()]

        for v in clean_values:
            result.append(f"• {v}")

        result.append("")  # ligne vide entre catégories

    return "\n".join(result) if result else "• Aucune compétence technique"

def format_competences_fonctionnelles(lst):
    if not isinstance(lst, list) or not lst:
        return "• Aucune compétence fonctionnelle"

    clean = [str(v).strip() for v in lst if v and str(v).strip()]

    if not clean:
        return "• Aucune compétence fonctionnelle"

    return "\n".join(f"• {v}" for v in clean)

def generate_cv_documents(cv_data: Dict, output_dir: str, filename: str = None) -> Dict[str, str]:
    """
    Génère les documents CV (DOCX et PDF) à partir des données structurées.
    
    Args:
        cv_data: Données CV structurées (contact, formations, experiences, etc.)
        output_dir: Dossier de sortie
        filename: Nom du fichier (sans extension)
    
    Returns:
        Dict avec les chemins des fichiers générés: {"docx": path, "pdf": path}
    """
    from datetime import datetime
    
    # Créer le dossier si nécessaire
    os.makedirs(output_dir, exist_ok=True)
    
    # Générer le nom de fichier
    if not filename:
        contact = cv_data.get("contact", {}) or {}
        nom = contact.get("nom", "CV")
        # Nettoyer le nom pour le fichier
        nom_clean = re.sub(r'[^\w\s-]', '', nom).strip().replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"CV_{nom_clean}_{timestamp}"
    
    docx_path = os.path.join(output_dir, f"{filename}.docx")
    pdf_path = os.path.join(output_dir, f"{filename}.pdf")
    
    result = {"docx": None, "pdf": None}
    
    # Générer le DOCX
    try:
        generate_sopra_docx(cv_data, docx_path)
        result["docx"] = docx_path
        print(f"✓ DOCX généré: {docx_path}")
    except Exception as e:
        print(f"❌ Erreur DOCX: {e}")
        raise
    
    # Générer le PDF
    try:
        from generators.docx_to_pdf import convert_docx_to_pdf
        convert_docx_to_pdf(docx_path, pdf_path)
        result["pdf"] = pdf_path
        print(f"✓ PDF généré: {pdf_path}")
    except ImportError:
        try:
            from docx_to_pdf import convert_docx_to_pdf
            convert_docx_to_pdf(docx_path, pdf_path)
            result["pdf"] = pdf_path
            print(f"✓ PDF généré: {pdf_path}")
        except Exception as e:
            print(f"⚠️ PDF non généré (docx2pdf indisponible): {e}")
    except Exception as e:
        print(f"⚠️ Erreur PDF: {e}")
    
    return result


def validate_cv_data(cv_data: Dict) -> List[str]:
    """
    Valide les données CV avant génération.
    
    Returns:
        Liste des avertissements/erreurs
    """
    warnings = []
    
    # Vérifier les champs obligatoires
    contact = cv_data.get("contact", {})
    if not contact:
        warnings.append("Contact manquant")
    else:
        if not contact.get("nom"):
            warnings.append("Nom manquant dans contact")
        if not contact.get("email"):
            warnings.append("Email manquant dans contact")
    
    # Vérifier les formations
    formations = cv_data.get("formations", [])
    if not formations:
        warnings.append("Aucune formation")
    else:
        for i, f in enumerate(formations):
            if not f.get("etablissement") and not f.get("diplome"):
                warnings.append(f"Formation {i+1}: établissement et diplôme manquants")
    
    # Vérifier les expériences
    experiences = cv_data.get("experiences", [])
    if not experiences:
        warnings.append("Aucune expérience")
    else:
        for i, e in enumerate(experiences):
            if not e.get("entreprise"):
                warnings.append(f"Expérience {i+1}: entreprise manquante")
    
    return warnings


def preview_cv_content(cv_data: Dict) -> str:
    """
    Génère un aperçu texte du contenu CV.
    """
    lines = []
    
    contact = cv_data.get("contact", {})
    lines.append(f"=== {contact.get('nom', 'N/A')} ===")
    lines.append(f"Email: {contact.get('email', 'N/A')}")
    lines.append(f"Tél: {contact.get('telephone', 'N/A')}")
    lines.append("")
    
    lines.append("--- FORMATIONS ---")
    for f in cv_data.get("formations", [])[:3]:
        lines.append(f"  • {f.get('diplome', 'N/A')} - {f.get('etablissement', 'N/A')}")
    
    lines.append("")
    lines.append("--- EXPÉRIENCES ---")
    for e in cv_data.get("experiences", [])[:3]:
        lines.append(f"  • {e.get('poste', 'N/A')} - {e.get('entreprise', 'N/A')}")
    
    lines.append("")
    lines.append("--- COMPÉTENCES ---")
    skills = cv_data.get("competences", [])[:10]
    lines.append(f"  {', '.join(skills) if skills else 'N/A'}")
    
    return "\n".join(lines)
