"""
Servicio de integración entre el backend y el módulo de IA.
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.models.sesion import Sesion
from backend.services.perfil_service import obtener_o_crear_perfil, actualizar_perfil, perfil_a_dict_para_ia

# Agregar el directorio raíz al path para importar el módulo ia
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def analizar_sesion(db: Session, usuario_id: str, sesion_data: dict) -> dict:
    """
    Orquesta el análisis de una sesión:
    1. Obtiene/actualiza perfil de comportamiento
    2. Recupera sesiones recientes
    3. Llama al módulo de IA
    4. Retorna el resultado
    """
    from ia.evaluar import evaluar_sesion

    # Actualizar perfil con datos recientes
    perfil_obj = actualizar_perfil(db, usuario_id)
    perfil_dict = perfil_a_dict_para_ia(perfil_obj)

    # Sesiones en las últimas 24h
    hace_24h = datetime.utcnow() - timedelta(hours=24)
    sesiones_recientes = db.query(Sesion).filter(
        Sesion.usuario_id == usuario_id,
        Sesion.fecha_hora >= hace_24h
    ).all()

    sesiones_para_ia = [s.to_dict() for s in sesiones_recientes]

    # Llamar al modelo de IA
    resultado = evaluar_sesion(sesion_data, perfil_dict, sesiones_para_ia)
    return resultado


def obtener_metricas_ia() -> dict:
    """Obtiene las métricas del modelo de IA."""
    from ia.metricas import obtener_metricas_modelo
    return obtener_metricas_modelo()
