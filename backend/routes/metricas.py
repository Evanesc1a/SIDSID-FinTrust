"""
Rutas para métricas del sistema y KPIs del negocio.
"""
from collections import defaultdict
from datetime import datetime, timedelta, timezone

_utcnow = lambda: datetime.now(timezone.utc).replace(tzinfo=None)
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from backend.config.database import SessionLocal
from backend.models.sesion import Sesion
from backend.models.alerta import Alerta
from backend.models.usuario import Usuario
from backend.services.ia_service import obtener_metricas_ia

metricas_bp = Blueprint("metricas", __name__, url_prefix="/api/metricas")


@metricas_bp.route("", methods=["GET"])
@jwt_required()
def get_metricas():
    db = SessionLocal()
    try:
        ahora = _utcnow()
        hace_24h = ahora - timedelta(hours=24)
        hace_7d = ahora - timedelta(days=7)

        # KPIs de sesiones (2 queries)
        total_sesiones_24h = db.query(Sesion).filter(Sesion.fecha_hora >= hace_24h).count()
        sesiones_anomalas_24h = db.query(Sesion).filter(
            Sesion.fecha_hora >= hace_24h, Sesion.es_anomala == 1
        ).count()

        # KPIs de alertas (3 queries escalares)
        alertas_nuevas = db.query(Alerta).filter(Alerta.estado == "NUEVA").count()
        alertas_criticas = db.query(Alerta).filter(
            Alerta.nivel_riesgo == "CRITICO", Alerta.estado == "NUEVA"
        ).count()
        alertas_7d = db.query(Alerta).filter(Alerta.fecha_creacion >= hace_7d).count()

        # Tiempo promedio de respuesta — solo columnas necesarias
        resueltas = db.query(Alerta.fecha_creacion, Alerta.fecha_resolucion).filter(
            Alerta.estado.in_(["RESUELTA", "DESCARTADA"]),
            Alerta.fecha_resolucion.isnot(None)
        ).all()
        tiempos = [
            (r.fecha_resolucion - r.fecha_creacion).total_seconds() / 60
            for r in resueltas
            if r.fecha_resolucion and r.fecha_creacion
        ]
        tiempo_promedio_respuesta = sum(tiempos) / len(tiempos) if tiempos else 0.0

        # Distribución por nivel — 1 query GROUP BY en lugar de 4 queries
        dist_rows = db.query(Alerta.nivel_riesgo, func.count(Alerta.id)).filter(
            Alerta.fecha_creacion >= hace_7d
        ).group_by(Alerta.nivel_riesgo).all()
        distribucion_nivel = {"BAJO": 0, "MEDIO": 0, "ALTO": 0, "CRITICO": 0}
        for nivel, count in dist_rows:
            if nivel in distribucion_nivel:
                distribucion_nivel[nivel] = count

        # Tendencia 7 días — 1 query + agrupación en Python en lugar de 7 queries
        sesiones_anomalas_7d = db.query(Sesion.fecha_hora).filter(
            Sesion.fecha_hora >= hace_7d,
            Sesion.es_anomala == 1
        ).all()
        count_por_dia: dict = defaultdict(int)
        for (fh,) in sesiones_anomalas_7d:
            count_por_dia[fh.strftime("%Y-%m-%d")] += 1

        tendencia = []
        for i in range(7, 0, -1):
            dia = (ahora - timedelta(days=i)).strftime("%Y-%m-%d")
            tendencia.append({"fecha": dia, "anomalas": count_por_dia.get(dia, 0)})

        # Usuarios (2 queries escalares)
        usuarios_activos = db.query(Usuario).filter_by(estado="ACTIVA").count()
        usuarios_bloqueados = db.query(Usuario).filter_by(estado="BLOQUEADA").count()

        metricas_ia = obtener_metricas_ia()

        return jsonify({
            "sesiones": {
                "total_24h": total_sesiones_24h,
                "anomalas_24h": sesiones_anomalas_24h,
                "tasa_anomalia": round(sesiones_anomalas_24h / max(total_sesiones_24h, 1) * 100, 1),
            },
            "alertas": {
                "nuevas": alertas_nuevas,
                "criticas": alertas_criticas,
                "ultimos_7d": alertas_7d,
                "distribucion_nivel": distribucion_nivel,
                "tiempo_promedio_respuesta_min": round(tiempo_promedio_respuesta, 1),
            },
            "usuarios": {
                "activos": usuarios_activos,
                "bloqueados": usuarios_bloqueados,
            },
            "tendencia_anomalias": tendencia,
            "modelo_ia": metricas_ia,
        }), 200
    finally:
        db.close()
