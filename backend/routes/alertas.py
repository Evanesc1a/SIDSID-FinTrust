"""
Rutas para gestión de alertas de seguridad.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.config.database import SessionLocal
from backend.services.alerta_service import (
    listar_alertas, obtener_alerta, resolver_alerta, contar_alertas_por_nivel
)
from backend.models.usuario import Usuario

alertas_bp = Blueprint("alertas", __name__, url_prefix="/api/alertas")


@alertas_bp.route("", methods=["GET"])
@jwt_required()
def get_alertas():
    estado = request.args.get("estado")
    nivel = request.args.get("nivel")
    limite = int(request.args.get("limite", 100))
    offset = int(request.args.get("offset", 0))

    db = SessionLocal()
    try:
        alertas = listar_alertas(db, estado=estado, nivel=nivel, limite=limite, offset=offset)
        
        # Enriquecer con nombre de usuario
        result = []
        for a in alertas:
            d = a.to_dict()
            usuario = db.query(Usuario).filter_by(id=a.usuario_id).first()
            d["usuario_nombre"] = usuario.nombre if usuario else "Desconocido"
            result.append(d)
        
        return jsonify(result), 200
    finally:
        db.close()


@alertas_bp.route("/<alerta_id>", methods=["GET"])
@jwt_required()
def get_alerta(alerta_id):
    db = SessionLocal()
    try:
        alerta = obtener_alerta(db, alerta_id)
        if not alerta:
            return jsonify({"error": "Alerta no encontrada"}), 404
        
        d = alerta.to_dict()
        usuario = db.query(Usuario).filter_by(id=alerta.usuario_id).first()
        d["usuario_nombre"] = usuario.nombre if usuario else "Desconocido"
        return jsonify(d), 200
    finally:
        db.close()


@alertas_bp.route("/<alerta_id>/resolver", methods=["PUT"])
@jwt_required()
def resolver(alerta_id):
    data = request.get_json() or {}
    identity = get_jwt_identity()
    accion = data.get("accion", "RESOLVER")  # RESOLVER | DESCARTAR
    notas = data.get("notas", "")

    db = SessionLocal()
    try:
        alerta = resolver_alerta(db, alerta_id, identity, accion, notas)
        if not alerta:
            return jsonify({"error": "Alerta no encontrada"}), 404
        return jsonify(alerta.to_dict()), 200
    finally:
        db.close()


@alertas_bp.route("/resumen", methods=["GET"])
@jwt_required()
def resumen():
    db = SessionLocal()
    try:
        conteo = contar_alertas_por_nivel(db)
        total_nuevas = sum(conteo.values())
        return jsonify({
            "por_nivel": conteo,
            "total_nuevas": total_nuevas,
        }), 200
    finally:
        db.close()
