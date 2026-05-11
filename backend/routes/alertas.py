from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from config.database import db
from models.alerta   import Alerta
from models.sesion   import Sesion
from models.entrenamiento import DatoEntrenamientoIA

alertas_bp = Blueprint("alertas", __name__)

NIVELES = {"MEDIO", "ALTO", "CRITICO"}


def _analista_id():
    identity = get_jwt_identity()
    return int(identity[2:]) if identity.startswith("a:") else None


@alertas_bp.route("", methods=["GET"])
@jwt_required()
def listar_alertas():
    """
    UC7 — Dashboard del analista.
    Query params: nivel, resuelta, decision, page, per_page
    """
    nivel    = request.args.get("nivel", "").upper()
    resuelta = request.args.get("resuelta")
    decision = request.args.get("decision", "").upper()
    page     = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)

    q = Alerta.query.order_by(Alerta.fecha_generacion.desc())
    if nivel in NIVELES:
        q = q.filter(Alerta.nivel_riesgo == nivel)
    if resuelta is not None:
        q = q.filter(Alerta.resuelta == (resuelta.lower() == "true"))
    if decision:
        q = q.filter(Alerta.decision_analista == decision)

    pagina = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "alertas":    [a.to_dict() for a in pagina.items],
        "total":      pagina.total,
        "pagina":     pagina.page,
        "paginas":    pagina.pages,
        "por_pagina": per_page,
    }), 200


@alertas_bp.route("/<int:aid>", methods=["GET"])
@jwt_required()
def obtener_alerta(aid):
    """Detalle con sesión y datos del usuario."""
    alerta = db.session.get(Alerta, aid)
    if not alerta:
        return jsonify({"error": "Alerta no encontrada"}), 404

    data = alerta.to_dict()
    if alerta.sesion:
        data["sesion"]  = alerta.sesion.to_dict()
        data["usuario"] = alerta.sesion.usuario.to_dict() if alerta.sesion.usuario else None
        # Features del modelo
        feat = alerta.sesion.dato_entrenamiento
        data["features"] = feat.to_dict() if feat else None
    return jsonify(data), 200


@alertas_bp.route("/<int:aid>/resolver", methods=["PUT"])
@jwt_required()
def resolver_alerta(aid):
    """
    UC8 — Validar alerta manualmente.
    Body: { decision, accion_tomada?, motivo_descarte? }
    decision: CONFIRMADO_FRAUDE | FALSO_POSITIVO | REQUIERE_MAS_INFO
    """
    alerta = db.session.get(Alerta, aid)
    if not alerta:
        return jsonify({"error": "Alerta no encontrada"}), 404
    if alerta.resuelta:
        return jsonify({"error": "La alerta ya fue resuelta"}), 409

    data     = request.get_json(silent=True) or {}
    decision = data.get("decision", "").upper()
    decisiones_validas = {"CONFIRMADO_FRAUDE", "FALSO_POSITIVO", "REQUIERE_MAS_INFO"}
    if decision not in decisiones_validas:
        return jsonify({"error": f"decision debe ser: {', '.join(decisiones_validas)}"}), 422

    analista_id = _analista_id()
    alerta.resuelta          = True
    alerta.decision_analista = decision
    alerta.analista_id       = analista_id
    alerta.accion_tomada     = data.get("accion_tomada", "ninguna")
    alerta.motivo_descarte   = data.get("motivo_descarte")
    alerta.fecha_resolucion  = datetime.now(timezone.utc)

    # Actualizar etiqueta de entrenamiento para retroalimentar el modelo
    feat = alerta.sesion.dato_entrenamiento if alerta.sesion else None
    if feat:
        feat.etiqueta_fraude = True if decision == "CONFIRMADO_FRAUDE" else False

    # Bloqueo automático si se confirma fraude con bloqueo
    if decision == "CONFIRMADO_FRAUDE" and alerta.accion_tomada in ("bloqueo_preventivo", "bloqueo_definitivo"):
        usuario = alerta.sesion.usuario if alerta.sesion else None
        if usuario:
            usuario.bloqueado      = True
            usuario.motivo_bloqueo = f"Fraude confirmado — Alerta #{aid}"

    db.session.commit()
    return jsonify(alerta.to_dict()), 200


@alertas_bp.route("/<int:aid>/asignar", methods=["PUT"])
@jwt_required()
def asignar_alerta(aid):
    """Asigna una alerta a un analista específico."""
    alerta = db.session.get(Alerta, aid)
    if not alerta:
        return jsonify({"error": "Alerta no encontrada"}), 404

    data = request.get_json(silent=True) or {}
    analista_id = data.get("analista_id") or _analista_id()
    alerta.analista_id = analista_id
    db.session.commit()
    return jsonify(alerta.to_dict()), 200
