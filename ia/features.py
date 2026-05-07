"""
Feature engineering para el modelo de detección de anomalías SIDSID.
Genera las 8 features definidas en el ARC42.
"""
import json
import numpy as np
from datetime import datetime, timedelta


def extraer_features(sesion_data: dict, perfil: dict, sesiones_recientes: list) -> dict:
    """
    Extrae las features de una sesión para alimentar el modelo Isolation Forest.
    
    Args:
        sesion_data: Datos de la sesión actual
        perfil: Perfil de comportamiento del usuario
        sesiones_recientes: Lista de sesiones de las últimas 24h
    
    Returns:
        Dict con las 8 features del modelo
    """
    fecha_hora = sesion_data.get("fecha_hora")
    if isinstance(fecha_hora, str):
        fecha_hora = datetime.fromisoformat(fecha_hora)
    elif fecha_hora is None:
        fecha_hora = datetime.utcnow()

    # Feature 1: hora_del_dia (0-23)
    hora_del_dia = fecha_hora.hour

    # Feature 2: dia_semana (0=lunes, 6=domingo)
    dia_semana = fecha_hora.weekday()

    # Feature 3: dispositivo_nuevo (0/1)
    dispositivos_frecuentes = _parse_json_list(perfil.get("dispositivos_frecuentes", "[]"))
    dispositivo_actual = sesion_data.get("dispositivo_id", "")
    dispositivo_nuevo = 0 if dispositivo_actual in dispositivos_frecuentes else 1

    # Feature 4: distancia_geo_aprox
    ubicaciones_habituales = _parse_json_list(perfil.get("ubicaciones_habituales", "[]"))
    ubicacion_actual = sesion_data.get("ubicacion", "")
    distancia_geo_aprox = 0.0 if ubicacion_actual in ubicaciones_habituales else 1.0
    # Escalar: si la ubicación es completamente desconocida = 2.0
    if ubicacion_actual and ubicacion_actual not in ubicaciones_habituales:
        distancia_geo_aprox = 2.0 if len(ubicaciones_habituales) > 0 else 0.5

    # Feature 5: sesiones_24h
    sesiones_24h = len(sesiones_recientes)

    # Feature 6: monto_relativo (transacciones de la sesión vs promedio histórico)
    monto_sesion = sesion_data.get("monto_sesion", 0.0)
    monto_promedio = perfil.get("monto_promedio_tx", 1.0) or 1.0
    monto_relativo = monto_sesion / monto_promedio if monto_promedio > 0 else 0.0

    # Feature 7: frecuencia_tx_sesion
    frecuencia_tx_sesion = sesion_data.get("num_transacciones", 0)

    # Feature 8: ip_nueva (0/1)
    ips_habituales = _parse_json_list(perfil.get("ips_habituales", "[]"))
    ip_actual = sesion_data.get("ip_acceso", "")
    ip_nueva = 0 if ip_actual in ips_habituales else 1

    features = {
        "hora_del_dia": hora_del_dia,
        "dia_semana": dia_semana,
        "dispositivo_nuevo": dispositivo_nuevo,
        "distancia_geo_aprox": distancia_geo_aprox,
        "sesiones_24h": sesiones_24h,
        "monto_relativo": monto_relativo,
        "frecuencia_tx_sesion": frecuencia_tx_sesion,
        "ip_nueva": ip_nueva,
    }
    return features


def features_a_array(features: dict) -> np.ndarray:
    """Convierte el dict de features a numpy array para el modelo."""
    keys = [
        "hora_del_dia", "dia_semana", "dispositivo_nuevo",
        "distancia_geo_aprox", "sesiones_24h", "monto_relativo",
        "frecuencia_tx_sesion", "ip_nueva"
    ]
    return np.array([[features[k] for k in keys]], dtype=float)


def calcular_factores_riesgo(features: dict) -> list:
    """Identifica los factores de riesgo más relevantes para la alerta."""
    factores = []

    if features["dispositivo_nuevo"] == 1:
        factores.append("Dispositivo no reconocido")
    if features["ip_nueva"] == 1:
        factores.append("IP de acceso inusual")
    if features["distancia_geo_aprox"] >= 2.0:
        factores.append("Ubicación geográfica atípica")
    if features["sesiones_24h"] > 5:
        factores.append(f"Alto número de sesiones en 24h ({int(features['sesiones_24h'])})")
    if features["monto_relativo"] > 3.0:
        factores.append(f"Monto transaccional {features['monto_relativo']:.1f}x sobre el promedio")
    if features["frecuencia_tx_sesion"] > 10:
        factores.append(f"Alta frecuencia de transacciones en sesión ({int(features['frecuencia_tx_sesion'])})")

    hora = features["hora_del_dia"]
    if hora < 5 or hora > 23:
        factores.append(f"Acceso en horario inusual ({int(hora)}:00h)")

    if not factores:
        factores.append("Combinación de patrones de comportamiento inusual")

    return factores


def _parse_json_list(value) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return []
    return []
