from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from config.database import db
from models.analista import Analista

analistas_bp = Blueprint("analistas", __name__)

def _require_supervisor():
    claims = get_jwt()
    if claims.get("rol") not in ("supervisor", "admin"):
        return jsonify({"error": "Se requiere rol supervisor o admin"}), 403
    return None

@analistas_bp.route("", methods=["GET"])
@jwt_required()
def listar_analistas():
    analistas = Analista.query.filter_by(activo=True).all()
    return jsonify([a.to_dict() for a in analistas]), 200

@analistas_bp.route("/<int:aid>", methods=["GET"])
@jwt_required()
def obtener_analista(aid):
    a = db.session.get(Analista, aid)
    return (jsonify(a.to_dict()), 200) if a else (jsonify({"error": "No encontrado"}), 404)
