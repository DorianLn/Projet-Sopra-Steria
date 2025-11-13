import sys
from pathlib import Path
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from generators.pdf_sopra_profile import generate_sopra_profile_pdf

# Ajoute le dossier parent au PYTHONPATH pour trouver analyser_cv.py
sys.path.append(str(Path(__file__).resolve().parent.parent))

from extractors.pdf_to_docx import convert_pdf_to_docx
from analyser_cv import lire_cv_docx, extraire_email, extraire_telephone, extraire_adresse, extraire_dates
from extractors.section_classifier import build_structured_json

app = Flask(__name__)
CORS(app)  # Autorise les requêtes cross-origin

UPLOAD_FOLDER = Path('data/input')
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_cv(file_path):
    """
    Traite un CV et retourne le JSON complet généré par build_structured_json
    """
    try:
        # Conversion PDF -> DOCX si nécessaire
        if file_path.suffix.lower() == '.pdf':
            temp_docx = file_path.parent / f"{file_path.stem}_temp.docx"
            if not convert_pdf_to_docx(str(file_path), str(temp_docx)):
                return None, "Erreur lors de la conversion PDF vers Word"
            file_path = temp_docx

        # Lecture du texte du CV
        texte_cv = lire_cv_docx(str(file_path))

        # Extraction regex
        emails = extraire_email(texte_cv)
        telephones = extraire_telephone(texte_cv)
        adresses = extraire_adresse(texte_cv)
        dates = extraire_dates(texte_cv)

        # Génération du JSON structuré
        resultats = build_structured_json(
            emails=emails,
            telephones=telephones,
            adresses=adresses,
            dates=dates,
            texte_cv=texte_cv
        )

        # Suppression du fichier temporaire si nécessaire
        if str(file_path).endswith('_temp.docx'):
            os.remove(file_path)

        return resultats, None
    except Exception as e:
        return None, str(e)


@app.route('/api/cv/analyze', methods=['POST'])
def analyze_cv():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier envoyé'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Type de fichier non autorisé (PDF ou DOCX uniquement)'}), 400

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        filename = secure_filename(file.filename)
        file_path = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(file_path))

        results, error = process_cv(file_path)

        if file_path.exists():
            os.remove(file_path)

        if error:
            return jsonify({'success': False, 'error': error}), 500

        # ----------------------
        # Génération automatique du PDF dynamique
        # ----------------------

        # Récupération du nom du candidat
        nom_candidat = (
            results.get("contact", {}).get("nom") or
            results.get("Nom") or
            results.get("nom") or
            "Inconnu"
        )

        # Nettoyage pour créer un nom de fichier valide
        nom_candidat = nom_candidat.replace(" ", "_").replace("/", "_")

        pdf_filename = f"CV_{nom_candidat}.pdf"
        pdf_path = Path("data/output") / pdf_filename


        os.makedirs("data/output", exist_ok=True)

        # Génération du PDF Sopra Steria
        generate_sopra_profile_pdf(results, str(pdf_path))

        # Ajouter le nom du PDF dans la réponse
        results["pdf_filename"] = pdf_filename

        return jsonify(results)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# -------------------------------------------------
# ROUTE DOWNLOAD — VERSION CORRIGÉE
# -------------------------------------------------
@app.route('/api/cv/pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    pdf_path = Path("data/output") / filename

    if not pdf_path.exists():
        return jsonify({'error': 'PDF introuvable'}), 404

    return send_file(
        str(pdf_path),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
