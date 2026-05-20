"""
Servicio para gestión de alertas de seguridad.
"""
import json
import uuid
from datetime import datetime, timezone

_utcnow = lambda: datetime.now(timezone.utc).replace(tzinfo=None)
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.models.alerta import Alerta


def crear_alerta(db: Session, usuario_id: str, sesion_id: str, resultado_ia: dict) -> Alerta:
    """Crea una nueva alerta basada en el resultado del análisis de IA.
    No hace commit — el llamador es responsable de confirmar la transacción.
    """
    alerta = Alerta(
        id=str(uuid.uuid4()),
        usuario_id=usuario_id,
        sesion_id=sesion_id,
        nivel_riesgo=resultado_ia["nivel_riesgo"],
        puntaje=resultado_ia["puntaje"],
        factores=json.dumps(resultado_ia.get("factores", [])),
        descripcion=_generar_descripcion(resultado_ia),
        estado="NUEVA",
        fecha_creacion=_utcnow(),
    )
    db.add(alerta)
    return alerta


def _generar_descripcion(resultado_ia: dict) -> str:
    nivel = resultado_ia["nivel_riesgo"]
    factores = resultado_ia.get("factores", [])
    desc = f"Acceso clasificado como riesgo {nivel}."
    if factores:
        desc += f" Factores detectados: {', '.join(factores[:3])}."
    return desc


def listar_alertas(db: Session, estado: str = None, nivel: str = None,
                   limite: int = 100, offset: int = 0) -> list:
    """Lista alertas con filtros opcionales."""
    query = db.query(Alerta)
    if estado:
        query = query.filter(Alerta.estado == estado)
    if nivel:
        query = query.filter(Alerta.nivel_riesgo == nivel)
    return query.order_by(desc(Alerta.fecha_creacion)).offset(offset).limit(limite).all()


def obtener_alerta(db: Session, alerta_id: str) -> Alerta:
    return db.query(Alerta).filter_by(id=alerta_id).first()


def resolver_alerta(db: Session, alerta_id: str, analista_id: str,
                    accion: str, notas: str = "") -> Alerta:
    """
    Resuelve o descarta una alerta.
    accion: 'RESOLVER' | 'DESCARTAR'
    """
    alerta = obtener_alerta(db, alerta_id)
    if not alerta:
        return None
    alerta.estado = "RESUELTA" if accion == "RESOLVER" else "DESCARTADA"
    alerta.analista_id = analista_id
    alerta.notas_analista = notas
    alerta.fecha_resolucion = _utcnow()
    db.commit()
    db.refresh(alerta)
    return alerta


def contar_alertas_por_nivel(db: Session) -> dict:
    """Retorna conteo de alertas activas por nivel (una sola query GROUP BY)."""
    rows = db.query(Alerta.nivel_riesgo, func.count(Alerta.id)).filter(
        Alerta.estado == "NUEVA"
    ).group_by(Alerta.nivel_riesgo).all()
    resultado = {"BAJO": 0, "MEDIO": 0, "ALTO": 0, "CRITICO": 0}
    for nivel, count in rows:
        if nivel in resultado:
            resultado[nivel] = count
    return resultado
