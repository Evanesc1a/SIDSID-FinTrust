from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from models.sesion   import Sesion
from models.alerta   import Alerta
from models.usuario  import Usuario

analisis_bp = Blueprint("analisis", __name__)


@analisis_bp.route("/analizar", methods=["POST"])
@jwt_required()
def analizar_sesion():
    """
    UC3-UC6 — Motor IA: analiza una sesión y genera alerta si procede.
    Body: { sesion_id }
    Semana 2: usa stub heurístico.
    Semana 3: reemplazar por Isolation Forest real (ia/evaluar.py).
    """
    data = request.get_json(silent=True) or {}
    sesion_id = data.get("sesion_id")
    if not sesion_id:
        return jsonify({"error": "sesion_id es requerido"}), 400

    sesion = db.session.get(Sesion, sesion_id)
    if not sesion:
        return jsonify({"error": "Sesión no encontrada"}), 404

    # Evitar doble análisis
    if sesion.puntaje_anomalia is not None:
        return jsonify({
            "mensaje":    "Sesión ya analizada",
            "sesion_id":  sesion_id,
            "nivel":      sesion.nivel_riesgo,
            "puntaje":    sesion.puntaje_anomalia,
        }), 200

    # ── Llamar al servicio IA ──────────────────────────────────────────────────
    from services.ia_service import analizar
    resultado = analizar(sesion)

    sesion.puntaje_anomalia = resultado["puntaje"]
    sesion.nivel_riesgo     = resultado["nivel"]
    sesion.es_anomala       = resultado["nivel"] != "BAJO"

    alerta_dict = None
    # Generar alerta si nivel ≥ MEDIO
    if resultado["nivel"] in ("MEDIO", "ALTO", "CRITICO"):
        alerta = Alerta(
            sesion_id    = sesion.id,
            nivel_riesgo = resultado["nivel"],
            descripcion  = resultado["descripcion"],
        )
        db.session.add(alerta)

        # Bloqueo automático en CRITICO
        if resultado["nivel"] == "CRITICO":
            usuario = db.session.get(Usuario, sesion.usuario_id)
            if usuario and not usuario.bloqueado:
                usuario.bloqueado      = True
                usuario.motivo_bloqueo = f"Bloqueo automático — sesión {sesion.id} CRITICO"

        db.session.flush()
        alerta_dict = alerta.to_dict()

    # Guardar features en datos_entrenamiento_ia
    from services.entrenamiento_service import guardar_features
    guardar_features(sesion, resultado)

    db.session.commit()
    return jsonify({
        "sesion_id":   sesion_id,
        "nivel":       resultado["nivel"],
        "puntaje":     resultado["puntaje"],
        "descripcion": resultado["descripcion"],
        "accion":      resultado.get("accion", "ninguna"),
        "alerta":      alerta_dict,
    }), 200
