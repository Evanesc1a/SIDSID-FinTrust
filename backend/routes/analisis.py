"""
Ruta para análisis directo de anomalías (POST /api/analizar).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.config.database import SessionLocal
from backend.services.ia_service import analizar_sesion

analisis_bp = Blueprint("analisis", __name__, url_prefix="/api")


@analisis_bp.route("/analizar", methods=["POST"])
@jwt_required()
def analizar():
    """Analiza una sesión sin registrarla en la BD."""
    data = request.get_json()
    if not data or not data.get("usuario_id"):
        return jsonify({"error": "usuario_id y datos de sesión requeridos"}), 400

    db = SessionLocal()
    try:
        resultado = analizar_sesion(db, data["usuario_id"], data)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
