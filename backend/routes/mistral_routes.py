"""
Endpoint Flask pour l'analyse de CV avec Mistral.
À intégrer dans votre api.py existant.
"""

from flask import Blueprint, request, jsonify
from extractors.mistral_analyzer import analyze_cv, verify_mistral_setup
import logging

logger = logging.getLogger(__name__)

# Créer un Blueprint pour l'analyse Mistral
mistral_bp = Blueprint('mistral', __name__, url_prefix='/api/mistral')


@mistral_bp.route('/status', methods=['GET'])
def mistral_status():
    """
    Endpoint pour vérifier l'état de Mistral.
    
    Returns:
        JSON avec l'état du setup Mistral
    """
    status = verify_mistral_setup()
    
    if status["status"] == "OK":
        return jsonify(status), 200
    else:
        return jsonify(status), 503


@mistral_bp.route('/analyze', methods=['POST'])
def mistral_analyze():
    """
    Endpoint pour analyser un CV avec Mistral.
    
    Expected JSON:
        {
            "cv_text": "Texte du CV à analyser"
        }
    
    Returns:
        JSON structuré avec les informations du CV
    """
    try:
        data = request.get_json()
        
        if not data or 'cv_text' not in data:
            return jsonify({
                "error": "Paramètre 'cv_text' manquant"
            }), 400
        
        cv_text = data['cv_text'].strip()
        
        if not cv_text:
            return jsonify({
                "error": "Le texte du CV ne peut pas être vide"
            }), 400
        
        # Analyser le CV
        result = analyze_cv(cv_text)
        
        if result is None:
            return jsonify({
                "error": "Erreur lors de l'analyse. Vérifiez que Ollama est lancé et Mistral téléchargé."
            }), 503
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse Mistral: {str(e)}")
        return jsonify({
            "error": f"Erreur serveur: {str(e)}"
        }), 500


@mistral_bp.route('/health', methods=['GET'])
def mistral_health():
    """
    Endpoint de health check pour Mistral.
    Retourne 200 si OK, 503 sinon.
    """
    status = verify_mistral_setup()
    
    if status["status"] == "OK":
        return jsonify({"status": "healthy"}), 200
    else:
        return jsonify({
            "status": "unhealthy",
            "details": status
        }), 503
