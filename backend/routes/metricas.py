from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from config.database import db
from models.alerta   import Alerta
from models.sesion   import Sesion
from models.usuario  import Usuario
from models.metrica  import MetricaModelo

metricas_bp = Blueprint("metricas", __name__)


@metricas_bp.route("", methods=["GET"])
@jwt_required()
def dashboard_kpis():
    """
    UC7 — KPIs del tablero principal.
    Totales de alertas, sesiones, usuarios bloqueados, tasas de detección y FP.
    """
    # Totales por nivel
    totales = (db.session.query(Alerta.nivel_riesgo, func.count(Alerta.id))
               .group_by(Alerta.nivel_riesgo).all())
    por_nivel = {n: c for n, c in totales}

    total_alertas      = sum(por_nivel.values())
    alertas_pendientes = Alerta.query.filter_by(resuelta=False).count()
    confirmadas        = Alerta.query.filter_by(decision_analista="CONFIRMADO_FRAUDE").count()
    falsos_positivos   = Alerta.query.filter_by(decision_analista="FALSO_POSITIVO").count()

    total_sesiones    = Sesion.query.count()
    sesiones_anomalas = Sesion.query.filter(Sesion.nivel_riesgo != "BAJO").count()
    usuarios_bloqueados = Usuario.query.filter_by(bloqueado=True).count()

    tasa_deteccion = round(sesiones_anomalas / total_sesiones * 100, 2) if total_sesiones else 0
    tasa_fp        = round(falsos_positivos / total_alertas * 100, 2) if total_alertas else 0

    # Última versión del modelo
    ultima_metrica = MetricaModelo.query.order_by(MetricaModelo.fecha_evaluacion.desc()).first()

    return jsonify({
        "alertas": {
            "total":      total_alertas,
            "pendientes": alertas_pendientes,
            "confirmadas":confirmadas,
            "falsos_positivos": falsos_positivos,
            "por_nivel": {
                "MEDIO":  por_nivel.get("MEDIO", 0),
                "ALTO":   por_nivel.get("ALTO", 0),
                "CRITICO":por_nivel.get("CRITICO", 0),
            },
        },
        "sesiones": {
            "total":     total_sesiones,
            "anomalas":  sesiones_anomalas,
            "tasa_deteccion_pct": tasa_deteccion,
        },
        "usuarios": {
            "bloqueados": usuarios_bloqueados,
        },
        "modelo": {
            "tasa_fp_pct":       tasa_fp,
            "ultima_version":    ultima_metrica.version_modelo if ultima_metrica else None,
            "f1_score":          ultima_metrica.f1_score if ultima_metrica else None,
            "precision":         ultima_metrica.precision_score if ultima_metrica else None,
            "recall":            ultima_metrica.recall_score if ultima_metrica else None,
        },
    }), 200


@metricas_bp.route("/modelo", methods=["GET"])
@jwt_required()
def historial_modelo():
    """Historial de versiones del modelo (UC métricas IA)."""
    metricas = MetricaModelo.query.order_by(MetricaModelo.fecha_evaluacion.desc()).all()
    return jsonify([m.to_dict() for m in metricas]), 200


@metricas_bp.route("/reporte-incidentes", methods=["GET"])
@jwt_required()
def reporte_incidentes():
    """UC12 — Reporte de incidentes por rango de fechas."""
    desde    = request.args.get("desde")
    hasta    = request.args.get("hasta")
    q = Alerta.query.filter_by(resuelta=True)
    if desde:
        q = q.filter(Alerta.fecha_generacion >= desde)
    if hasta:
        q = q.filter(Alerta.fecha_generacion <= hasta)
    alertas = q.order_by(Alerta.fecha_generacion.desc()).all()
    return jsonify({"total": len(alertas), "desde": desde, "hasta": hasta,
                    "registros": [a.to_dict() for a in alertas]}), 200
