from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from config.database import db
from models.usuario  import Usuario
from models.alerta   import Alerta
from models.sesion   import Sesion

usuarios_bp = Blueprint("usuarios", __name__)


def _require_analista():
    claims = get_jwt()
    if claims.get("tipo") != "analista":
        return jsonify({"error": "Solo analistas pueden realizar esta acción"}), 403
    return None


@usuarios_bp.route("", methods=["GET"])
@jwt_required()
def listar_usuarios():
    """Lista usuarios con filtros opcionales. Solo analistas."""
    err = _require_analista()
    if err: return err

    bloqueado = request.args.get("bloqueado")
    segmento  = request.args.get("segmento")
    page      = int(request.args.get("page", 1))
    per_page  = int(request.args.get("per_page", 20))
    q = Usuario.query.order_by(Usuario.fecha_creacion.desc())
    if bloqueado is not None:
        q = q.filter(Usuario.bloqueado == (bloqueado.lower() == "true"))
    if segmento:
        q = q.filter(Usuario.segmento == segmento)
    pagina = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "usuarios": [u.to_dict() for u in pagina.items],
        "total":    pagina.total,
        "pagina":   pagina.page,
        "paginas":  pagina.pages,
    }), 200


@usuarios_bp.route("/<int:uid>", methods=["GET"])
@jwt_required()
def obtener_usuario(uid):
    u = db.session.get(Usuario, uid)
    if not u: return jsonify({"error": "No encontrado"}), 404
    data = u.to_dict()
    data["perfil"] = u.perfil.to_dict() if u.perfil else {}
    return jsonify(data), 200


@usuarios_bp.route("/<int:uid>/bloquear", methods=["POST"])
@jwt_required()
def bloquear_usuario(uid):
    """UC10 — Bloqueo preventivo. Solo analistas."""
    err = _require_analista()
    if err: return err

    u = db.session.get(Usuario, uid)
    if not u: return jsonify({"error": "No encontrado"}), 404
    data = request.get_json(silent=True) or {}
    u.bloqueado      = True
    u.motivo_bloqueo = data.get("motivo", "Bloqueo preventivo por el analista")
    db.session.commit()
    return jsonify({"mensaje": "Cuenta bloqueada", "usuario": u.to_dict()}), 200


@usuarios_bp.route("/<int:uid>/desbloquear", methods=["POST"])
@jwt_required()
def desbloquear_usuario(uid):
    """Desbloquea una cuenta. Solo analistas."""
    err = _require_analista()
    if err: return err

    u = db.session.get(Usuario, uid)
    if not u: return jsonify({"error": "No encontrado"}), 404
    u.bloqueado      = False
    u.motivo_bloqueo = None
    db.session.commit()
    return jsonify({"mensaje": "Cuenta desbloqueada", "usuario": u.to_dict()}), 200


@usuarios_bp.route("/<int:uid>/historial-alertas", methods=["GET"])
@jwt_required()
def historial_alertas(uid):
    """UC11 — Historial de alertas del usuario."""
    u = db.session.get(Usuario, uid)
    if not u: return jsonify({"error": "No encontrado"}), 404

    sesion_ids = [s.id for s in u.sesiones.all()]
    alertas = (Alerta.query
               .filter(Alerta.sesion_id.in_(sesion_ids))
               .order_by(Alerta.fecha_generacion.desc())
               .all())
    return jsonify([a.to_dict() for a in alertas]), 200


@usuarios_bp.route("/<int:uid>/autenticacion-reforzada", methods=["POST"])
@jwt_required()
def auth_reforzada(uid):
    """UC9 — Solicitar OTP. Retorna OTP simulado (dev). En prod: enviar por SMS/email."""
    import random, string
    otp = "".join(random.choices(string.digits, k=6))
    return jsonify({
        "mensaje":       "OTP generado",
        "usuario_id":    uid,
        "otp_simulado":  otp,     # ELIMINAR en producción
        "expira_en_seg": 300,
    }), 200
