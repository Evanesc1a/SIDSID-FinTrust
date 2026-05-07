"""
Rutas para registro y consulta de sesiones digitales.
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from backend.config.database import SessionLocal
from backend.models.sesion import Sesion
from backend.models.transaccion import Transaccion
from backend.services.ia_service import analizar_sesion
from backend.services.alerta_service import crear_alerta

sesiones_bp = Blueprint("sesiones", __name__, url_prefix="/api/sesiones")


@sesiones_bp.route("", methods=["POST"])
@jwt_required()
def registrar_sesion():
    """Registra una nueva sesión y ejecuta el análisis de anomalías."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos requeridos"}), 400

    usuario_id = data.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "usuario_id requerido"}), 400

    db = SessionLocal()
    try:
        sesion = Sesion(
            id=str(uuid.uuid4()),
            usuario_id=usuario_id,
            fecha_hora=datetime.utcnow(),
            dispositivo_id=data.get("dispositivo_id", "unknown"),
            ubicacion=data.get("ubicacion", ""),
            ip_acceso=data.get("ip_acceso", "0.0.0.0"),
            duracion_min=data.get("duracion_min", 0),
            tipo_acceso=data.get("tipo_acceso", "web"),
        )
        db.add(sesion)
        db.flush()  # para tener el ID antes del análisis

        # Agregar datos de transacciones a sesion_data para features
        sesion_data = {
            "id": sesion.id,
            "usuario_id": usuario_id,
            "fecha_hora": sesion.fecha_hora.isoformat(),
            "dispositivo_id": sesion.dispositivo_id,
            "ubicacion": sesion.ubicacion,
            "ip_acceso": sesion.ip_acceso,
            "monto_sesion": data.get("monto_sesion", 0.0),
            "num_transacciones": data.get("num_transacciones", 0),
        }

        # Análisis de IA
        resultado = analizar_sesion(db, usuario_id, sesion_data)

        # Actualizar sesión con resultado
        sesion.puntaje_anomalia = resultado["puntaje"]
        sesion.es_anomala = 1 if resultado["es_anomala"] else 0
        sesion.nivel_riesgo = resultado["nivel_riesgo"]

        # Crear alerta si el nivel es MEDIO o superior
        alerta = None
        if resultado["nivel_riesgo"] in ("MEDIO", "ALTO", "CRITICO"):
            alerta = crear_alerta(db, usuario_id, sesion.id, resultado)

        db.commit()

        response = {
            "sesion": sesion.to_dict(),
            "analisis": {
                "puntaje": float(resultado["puntaje"]),
                "es_anomala": bool(resultado["es_anomala"]),
                "nivel_riesgo": resultado["nivel_riesgo"],
                "factores": resultado["factores"],
            },
            "alerta_creada": alerta.to_dict() if alerta else None,
        }
        return jsonify(response), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@sesiones_bp.route("", methods=["GET"])
@jwt_required()
def listar_sesiones():
    usuario_id = request.args.get("usuario_id")
    limite = int(request.args.get("limite", 50))

    db = SessionLocal()
    try:
        query = db.query(Sesion)
        if usuario_id:
            query = query.filter(Sesion.usuario_id == usuario_id)
        sesiones = query.order_by(desc(Sesion.fecha_hora)).limit(limite).all()
        return jsonify([s.to_dict() for s in sesiones]), 200
    finally:
        db.close()


@sesiones_bp.route("/<sesion_id>", methods=["GET"])
@jwt_required()
def obtener_sesion(sesion_id):
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(id=sesion_id).first()
        if not sesion:
            return jsonify({"error": "Sesión no encontrada"}), 404
        return jsonify(sesion.to_dict()), 200
    finally:
        db.close()
