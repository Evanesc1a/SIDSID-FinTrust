"""
Servicio para gestión de perfiles de comportamiento de usuarios.
"""
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.models.perfil import PerfilComportamiento
from backend.models.sesion import Sesion
from backend.models.transaccion import Transaccion


def obtener_o_crear_perfil(db: Session, usuario_id: str) -> PerfilComportamiento:
    """Obtiene el perfil de un usuario, creándolo si no existe."""
    perfil = db.query(PerfilComportamiento).filter_by(usuario_id=usuario_id).first()
    if not perfil:
        perfil = PerfilComportamiento(usuario_id=usuario_id)
        db.add(perfil)
        db.commit()
        db.refresh(perfil)
    return perfil


def actualizar_perfil(db: Session, usuario_id: str) -> PerfilComportamiento:
    """Recalcula y actualiza el perfil de comportamiento del usuario."""
    perfil = obtener_o_crear_perfil(db, usuario_id)

    # Sesiones históricas (últimas 30 días)
    hace_30_dias = datetime.utcnow() - timedelta(days=30)
    sesiones = db.query(Sesion).filter(
        Sesion.usuario_id == usuario_id,
        Sesion.fecha_hora >= hace_30_dias
    ).all()

    # Transacciones históricas
    transacciones = db.query(Transaccion).filter(
        Transaccion.usuario_id == usuario_id,
        Transaccion.fecha_hora >= hace_30_dias
    ).all()

    # Dispositivos frecuentes
    dispositivos = list(set(s.dispositivo_id for s in sesiones if s.dispositivo_id))
    
    # Horarios habituales (horas con al menos 2 accesos)
    from collections import Counter
    horas = Counter(s.fecha_hora.hour for s in sesiones if s.fecha_hora)
    horarios = [h for h, count in horas.items() if count >= 2]

    # Ubicaciones habituales
    ubicaciones = list(set(s.ubicacion for s in sesiones if s.ubicacion))

    # IPs habituales
    ips = list(set(s.ip_acceso for s in sesiones if s.ip_acceso))

    # Métricas de transacciones
    montos = [t.monto for t in transacciones if t.monto]
    monto_promedio = sum(montos) / len(montos) if montos else 0.0
    
    # Frecuencia promedio de transacciones por sesión
    frecuencia_tx = len(transacciones) / max(len(sesiones), 1)

    # Sesiones promedio por día
    sesiones_por_dia = len(sesiones) / 30.0

    # Actualizar perfil
    perfil.dispositivos_frecuentes = json.dumps(dispositivos)
    perfil.horarios_habituales = json.dumps(horarios)
    perfil.ubicaciones_habituales = json.dumps(ubicaciones)
    perfil.ips_habituales = json.dumps(ips)
    perfil.monto_promedio_tx = monto_promedio
    perfil.frecuencia_tx = frecuencia_tx
    perfil.sesiones_promedio_dia = sesiones_por_dia
    perfil.ultima_actualizacion = datetime.utcnow()

    db.commit()
    db.refresh(perfil)
    return perfil


def perfil_a_dict_para_ia(perfil: PerfilComportamiento) -> dict:
    """Convierte el perfil a un dict compatible con el módulo de IA."""
    return {
        "dispositivos_frecuentes": perfil.dispositivos_frecuentes,
        "ubicaciones_habituales": perfil.ubicaciones_habituales,
        "ips_habituales": perfil.ips_habituales,
        "monto_promedio_tx": perfil.monto_promedio_tx or 1.0,
        "frecuencia_tx": perfil.frecuencia_tx or 1.0,
        "sesiones_promedio_dia": perfil.sesiones_promedio_dia or 1.0,
    }
