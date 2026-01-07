import sys
from pathlib import Path
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from generators.pdf_sopra_profile import generate_sopra_profile_pdf
import json
import logging
logging.basicConfig(level=logging.DEBUG)



# Ajoute le dossier parent au PYTHONPATH pour trouver analyser_cv.py
sys.path.append(str(Path(__file__).resolve().parent.parent))

from extractors.pdf_to_docx import convert_pdf_to_docx
from analyser_cv import lire_cv_docx, extraire_infos_cv
from extractors.section_classifier import build_structured_json

app = Flask(__name__)
CORS(app)  # Autorise les requêtes cross-origin

UPLOAD_FOLDER = Path('data/input')
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_cv(file_path):
    try:
        # Conversion si PDF → DOCX
        if file_path.suffix.lower() == '.pdf':
            temp_docx = file_path.parent / f"{file_path.stem}_temp.docx"
            if not convert_pdf_to_docx(str(file_path), str(temp_docx)):
                return None, "Erreur PDF -> DOCX"
            file_path = temp_docx

        # Lecture du DOCX
        texte_cv = lire_cv_docx(str(file_path))

        # Appel de la même fonction que le script CLI
        infos_brutes = extraire_infos_cv(texte_cv)

        # Build complet + classification + SpaCy
        resultats = build_structured_json(
            emails=infos_brutes["emails"],
            telephones=infos_brutes["telephones"],
            adresses=infos_brutes["adresses"],
            dates=infos_brutes["dates"],
            texte_cv=texte_cv
        )

        # Sauvegarde JSON propre
        nom_candidat = (resultats.get("contact", {}).get("nom") or "Inconnu").replace(" ", "_")
        json_filename = f"CV_{nom_candidat}.json"
        json_path = Path("data/output") / json_filename

        os.makedirs("data/output", exist_ok=True) 

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(resultats, f, ensure_ascii=False, indent=2)

        resultats["json_filename"] = json_filename


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
#           ROUTE DOWNLOAD DOCX       
# -------------------------------------------------
@app.route('/api/cv/docx/<filename>', methods=['GET'])
def download_docx(filename):
    from generators.generate_sopra_docx import generate_sopra_docx
    
    base = Path("data/output")
    json_path = base / f"{filename}.json"
    docx_path = base / f"{filename}.docx"

    if not json_path.exists():
        return jsonify({"error": "JSON introuvable"}), 404

    # Charger JSON
    cv_data = json.loads(json_path.read_text(encoding='utf-8'))

    # Générer DOCX
    generate_sopra_docx(cv_data, str(docx_path))

    return send_file(
        str(docx_path),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=f"{filename}.docx"
    )

# -------------------------------------------------
#           ROUTE CONVERT DOCX TO PDF
# -------------------------------------------------
@app.route('/api/cv/convert', methods=['POST'])
def convert_docx_to_pdf_route():
    from generators.docx_to_pdf import convert_docx_to_pdf

    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier envoyé"}), 400

        file = request.files['file']
        filename = secure_filename(file.filename)

        if not filename.endswith('.docx'):
            return jsonify({"error": "Veuillez envoyer un fichier .docx"}), 400

        temp_docx = Path("data/input") / filename
        file.save(temp_docx)

        output_pdf = Path("data/output") / f"{temp_docx.stem}_modified.pdf"

        convert_docx_to_pdf(str(temp_docx), str(output_pdf))

        return send_file(
            str(output_pdf),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{temp_docx.stem}_modified.pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------
#                ROUTE DOWNLOAD PDF
# -------------------------------------------------
@app.route('/api/cv/pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    from generators.generate_sopra_docx import generate_sopra_docx
    from generators.docx_to_pdf import convert_docx_to_pdf

    base = Path("data/output")

    # -----------------------------------------------------
    #  MODE A — PDF déjà généré dans /analyze
    # -----------------------------------------------------
    if filename.endswith(".pdf"):
        pdf_path = base / filename
        if pdf_path.exists():
            return send_file(
                str(pdf_path),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=filename
            )
        return jsonify({"error": "PDF déjà généré introuvable"}), 404

    # -----------------------------------------------------
    #  MODE B — Recréation du PDF à partir du JSON
    # -----------------------------------------------------
    json_path = base / f"{filename}.json"
    docx_path = base / f"{filename}.docx"
    pdf_path  = base / f"{filename}.pdf"

    if not json_path.exists():
        return jsonify({"error": "JSON introuvable"}), 404

    # Charger JSON
    cv_data = json.loads(json_path.read_text(encoding="utf-8"))

    # Générer DOCX
    generate_sopra_docx(cv_data, str(docx_path))

    # Convertir en PDF
    convert_docx_to_pdf(str(docx_path), str(pdf_path))

    # Télécharger PDF final
    return send_file(
        str(pdf_path),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{filename}.pdf"
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
