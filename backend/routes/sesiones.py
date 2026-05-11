from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from config.database import db
from models.sesion      import Sesion
from models.transaccion import Transaccion

sesiones_bp = Blueprint("sesiones", __name__)


def _get_usuario_id():
    identity = get_jwt_identity()
    if identity.startswith("u:"):
        return int(identity[2:])
    return None


@sesiones_bp.route("", methods=["POST"])
@jwt_required()
def crear_sesion():
    """
    UC2 — Registrar sesión exitosa con contexto de dispositivo/red.
    Body: { ip?, dispositivo?, ubicacion?, latitud?, longitud? }
    """
    uid = _get_usuario_id()
    if not uid:
        return jsonify({"error": "Solo usuarios pueden crear sesiones"}), 403

    data   = request.get_json(silent=True) or {}
    sesion = Sesion(
        usuario_id  = uid,
        ip          = data.get("ip") or request.remote_addr,
        dispositivo = data.get("dispositivo"),
        ubicacion   = data.get("ubicacion"),
        latitud     = data.get("latitud"),
        longitud    = data.get("longitud"),
    )
    db.session.add(sesion)
    db.session.commit()
    return jsonify(sesion.to_dict()), 201


@sesiones_bp.route("/<int:sid>", methods=["GET"])
@jwt_required()
def obtener_sesion(sid):
    sesion = db.session.get(Sesion, sid)
    if not sesion:
        return jsonify({"error": "Sesión no encontrada"}), 404
    data = sesion.to_dict()
    data["transacciones"] = [t.to_dict() for t in sesion.transacciones.all()]
    return jsonify(data), 200


@sesiones_bp.route("/<int:sid>/cerrar", methods=["PUT"])
@jwt_required()
def cerrar_sesion(sid):
    """Marca hora_fin de la sesión."""
    sesion = db.session.get(Sesion, sid)
    if not sesion:
        return jsonify({"error": "Sesión no encontrada"}), 404
    sesion.hora_fin = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(sesion.to_dict()), 200


@sesiones_bp.route("/<int:sid>/transacciones", methods=["POST"])
@jwt_required()
def crear_transaccion(sid):
    """
    UC13 — Registrar transacción dentro de una sesión activa.
    Body: { tipo, monto, descripcion? }
    """
    sesion = db.session.get(Sesion, sid)
    if not sesion:
        return jsonify({"error": "Sesión no encontrada"}), 404

    data = request.get_json(silent=True) or {}
    if not data.get("tipo") or not data.get("monto"):
        return jsonify({"error": "tipo y monto son requeridos"}), 400

    tipos_validos = {"pago", "transferencia", "recarga", "retiro", "credito"}
    if data["tipo"] not in tipos_validos:
        return jsonify({"error": f"tipo debe ser uno de: {', '.join(tipos_validos)}"}), 422

    tx = Transaccion(
        sesion_id   = sid,
        tipo        = data["tipo"],
        monto       = data["monto"],
        descripcion = data.get("descripcion"),
        estado      = data.get("estado", "pendiente"),
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify(tx.to_dict()), 201


@sesiones_bp.route("/<int:sid>/transacciones", methods=["GET"])
@jwt_required()
def listar_transacciones(sid):
    sesion = db.session.get(Sesion, sid)
    if not sesion:
        return jsonify({"error": "Sesión no encontrada"}), 404
    return jsonify([t.to_dict() for t in sesion.transacciones.order_by(Transaccion.hora.desc()).all()]), 200


@sesiones_bp.route("/usuario/<int:uid>", methods=["GET"])
@jwt_required()
def sesiones_de_usuario(uid):
    """Lista las últimas sesiones de un usuario (útil para el analista)."""
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    pagina   = (Sesion.query
                .filter_by(usuario_id=uid)
                .order_by(Sesion.hora_inicio.desc())
                .paginate(page=page, per_page=per_page, error_out=False))
    return jsonify({
        "sesiones":  [s.to_dict() for s in pagina.items],
        "total":     pagina.total,
        "pagina":    pagina.page,
        "paginas":   pagina.pages,
    }), 200
