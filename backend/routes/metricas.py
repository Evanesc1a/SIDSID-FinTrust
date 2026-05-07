"""
Rutas para métricas del sistema y KPIs del negocio.
"""
from datetime import datetime, timedelta
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
        ahora = datetime.utcnow()
        hace_24h = ahora - timedelta(hours=24)
        hace_7d = ahora - timedelta(days=7)

        # KPIs de sesiones
        total_sesiones_24h = db.query(Sesion).filter(Sesion.fecha_hora >= hace_24h).count()
        sesiones_anomalas_24h = db.query(Sesion).filter(
            Sesion.fecha_hora >= hace_24h, Sesion.es_anomala == 1
        ).count()

        # KPIs de alertas
        alertas_nuevas = db.query(Alerta).filter(Alerta.estado == "NUEVA").count()
        alertas_criticas = db.query(Alerta).filter(
            Alerta.nivel_riesgo == "CRITICO", Alerta.estado == "NUEVA"
        ).count()
        alertas_7d = db.query(Alerta).filter(Alerta.fecha_creacion >= hace_7d).count()
        
        # Alertas resueltas (para calcular tiempo promedio de respuesta)
        alertas_resueltas = db.query(Alerta).filter(
            Alerta.estado.in_(["RESUELTA", "DESCARTADA"]),
            Alerta.fecha_resolucion.isnot(None)
        ).all()
        
        tiempos = []
        for a in alertas_resueltas:
            if a.fecha_resolucion and a.fecha_creacion:
                diff = (a.fecha_resolucion - a.fecha_creacion).total_seconds() / 60
                tiempos.append(diff)
        tiempo_promedio_respuesta = sum(tiempos) / len(tiempos) if tiempos else 0.0

        # Distribución de alertas por nivel (últimos 7 días)
        distribucion_nivel = {}
        for nivel in ["BAJO", "MEDIO", "ALTO", "CRITICO"]:
            distribucion_nivel[nivel] = db.query(Alerta).filter(
                Alerta.nivel_riesgo == nivel,
                Alerta.fecha_creacion >= hace_7d
            ).count()

        # Tendencia de sesiones anómalas (últimos 7 días, por día)
        tendencia = []
        for i in range(7):
            dia_inicio = ahora - timedelta(days=i+1)
            dia_fin = ahora - timedelta(days=i)
            count = db.query(Sesion).filter(
                Sesion.fecha_hora >= dia_inicio,
                Sesion.fecha_hora < dia_fin,
                Sesion.es_anomala == 1
            ).count()
            tendencia.append({
                "fecha": dia_inicio.strftime("%Y-%m-%d"),
                "anomalas": count,
            })
        tendencia.reverse()

        # Usuarios activos
        usuarios_activos = db.query(Usuario).filter_by(estado="ACTIVA").count()
        usuarios_bloqueados = db.query(Usuario).filter_by(estado="BLOQUEADA").count()

        # Métricas del modelo IA
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
