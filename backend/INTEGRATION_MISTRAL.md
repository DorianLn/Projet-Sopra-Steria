"""
INSTRUCTIONS D'INTÉGRATION DE MISTRAL DANS api.py

Copiez-collez ce code dans votre api.py existant.
"""

# ============================================================================
# À AJOUTER APRÈS LES IMPORTS EXISTANTS (environ ligne 20)
# ============================================================================

# from extractors.mistral_analyzer import analyze_cv as mistral_analyze_cv, verify_mistral_setup


# ============================================================================
# À AJOUTER APRÈS LA CRÉATION DE L'APP (environ ligne 30-50)
# ============================================================================

# # Enregistrer les routes Mistral
# from routes.mistral_routes import mistral_bp
# app.register_blueprint(mistral_bp)


# ============================================================================
# OPTION A: AJOUTER UN ENDPOINT POUR ANALYSER AVEC MISTRAL
# ============================================================================

# @app.route('/api/cv/analyze-mistral', methods=['POST'])
# def analyze_cv_mistral():
#     """
#     Endpoint pour analyser un CV avec Mistral.
#     Accepte le texte directement au lieu d'un fichier.
#     
#     JSON Input:
#         {
#             "cv_text": "Texte du CV"
#         }
#     """
#     try:
#         data = request.get_json()
#         
#         if not data or 'cv_text' not in data:
#             return jsonify({
#                 'success': False,
#                 'error': 'Paramètre cv_text manquant'
#             }), 400
#         
#         cv_text = data['cv_text'].strip()
#         
#         if not cv_text:
#             return jsonify({
#                 'success': False,
#                 'error': 'Le texte du CV ne peut pas être vide'
#             }), 400
#         
#         # Analyser avec Mistral
#         result = mistral_analyze_cv(cv_text)
#         
#         if result is None:
#             return jsonify({
#                 'success': False,
#                 'error': 'Erreur lors de l\'analyse. Vérifiez qu\'Ollama est lancé.'
#             }), 503
#         
#         return jsonify({
#             'success': True,
#             'data': result
#         }), 200
#         
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': f'Erreur serveur: {str(e)}'
#         }), 500


# ============================================================================
# OPTION B: COMBINER AVEC VOTRE ANALYSE EXISTANTE
# ============================================================================

# @app.route('/api/cv/analyze-hybrid', methods=['POST'])
# def analyze_cv_hybrid():
#     """
#     Analyse un CV en combinant:
#     1. Extraction classique (regex/spacy)
#     2. Analyse Mistral pour plus de précision
#     """
#     if 'file' not in request.files:
#         return jsonify({'success': False, 'error': 'Aucun fichier envoyé'}), 400
#     
#     file = request.files['file']
#     
#     if file.filename == '' or not allowed_file(file.filename):
#         return jsonify({'success': False, 'error': 'Fichier invalide'}), 400
#     
#     try:
#         os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#         filename = secure_filename(file.filename)
#         file_path = Path(app.config['UPLOAD_FOLDER']) / filename
#         file.save(str(file_path))
#         
#         # Étape 1: Traitement classique
#         if file_path.suffix.lower() == '.pdf':
#             temp_docx = file_path.parent / f"{file_path.stem}_temp.docx"
#             if not convert_pdf_to_docx(str(file_path), str(temp_docx)):
#                 return jsonify({'success': False, 'error': 'Erreur PDF -> DOCX'}), 400
#             file_path = temp_docx
#         
#         texte_cv = lire_cv_docx(str(file_path))
#         
#         # Étape 2: Analyse Mistral
#         mistral_result = mistral_analyze_cv(texte_cv)
#         
#         if mistral_result is None:
#             # Fallback sur l'analyse classique
#             logging.warning("Mistral indisponible, utilisation de l'analyse classique")
#             infos_brutes = extraire_infos_cv(texte_cv)
#             resultats = build_structured_json(
#                 emails=infos_brutes["emails"],
#                 telephones=infos_brutes["telephones"],
#                 adresses=infos_brutes["adresses"],
#                 dates=infos_brutes["dates"],
#                 texte_cv=texte_cv
#             )
#             resultats['analysis_method'] = 'classical'
#         else:
#             # Utiliser les résultats Mistral
#             resultats = mistral_result
#             resultats['analysis_method'] = 'mistral'
#         
#         # Nettoyer les fichiers temp
#         if str(file_path).endswith('_temp.docx'):
#             os.remove(file_path)
#         
#         return jsonify({
#             'success': True,
#             'data': resultats,
#             'method': resultats.get('analysis_method', 'unknown')
#         }), 200
#         
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500


# ============================================================================
# À AJOUTER POUR LES HEALTH CHECKS
# ============================================================================

# @app.route('/api/health', methods=['GET'])
# def health():
#     """Health check complet du serveur."""
#     status = {
#         'status': 'OK',
#         'api': 'running',
#         'mistral': verify_mistral_setup()
#     }
#     
#     if status['mistral']['status'] != 'OK':
#         status['status'] = 'DEGRADED'
#     
#     return jsonify(status), 200


# ============================================================================
# EXEMPLE DE CURL POUR TESTER
# ============================================================================

"""
# Test de Mistral:
curl -X POST http://localhost:5000/api/mistral/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Jean Dupont\nEmail: jean@example.com\nDéveloppeur Python"
  }'

# Test du statut Mistral:
curl http://localhost:5000/api/mistral/status

# Test hybrid (avec fichier):
curl -X POST http://localhost:5000/api/cv/analyze-hybrid \
  -F "file=@/path/to/cv.pdf"
"""


# ============================================================================
# SI VOUS VOULEZ UTILISER MISTRAL DIRECTEMENT EN PYTHON
# ============================================================================

"""
from extractors.mistral_analyzer import MistralCVAnalyzer

# Utilisation simple
analyzer = MistralCVAnalyzer()

cv_text = "..."
result = analyzer.analyze_cv(cv_text)

if result:
    print("Analyse réussie:", result)
else:
    print("Erreur lors de l'analyse")
"""
