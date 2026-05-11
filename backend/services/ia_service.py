"""
services/ia_service.py
──────────────────────
Semana 2 → stub heurístico (completamente funcional sin modelo entrenado).
Semana 3 → reemplazar analizar() por la llamada real a ia/evaluar.py.

El puntaje sigue la convención de Isolation Forest:
  valores negativos = más anómalo   (-1.0 … 0.0)
  valores positivos = más normal    (0.0 … +1.0)
"""
import math
import random


# ── Constantes de umbral (se sincronizan con .env en Semana 3) ───────────────
# Corresponden al puntaje normalizado entre 0 y 1 (absoluto del score negativo)
UMBRAL_MEDIO   = 0.30
UMBRAL_ALTO    = 0.55
UMBRAL_CRITICO = 0.80


# ─── API pública ─────────────────────────────────────────────────────────────

def analizar(sesion) -> dict:
    """
    Punto de entrada principal.
    Semana 3: descomenta la llamada al modelo real y elimina el stub.
    """
    # ── Semana 3: modelo real ─────────────────────────────────────────────────
    # return _analizar_con_modelo(sesion)

    # ── Semana 2: stub heurístico ─────────────────────────────────────────────
    return _analizar_stub(sesion)


# ─── STUB ────────────────────────────────────────────────────────────────────

def _analizar_stub(sesion) -> dict:
    """
    Heurística multi-factor para clasificar sesiones sin modelo entrenado.
    Cada factor detectado incrementa el puntaje de anomalía.
    """
    factores   = []
    score_base = 0.05   # sesión perfectamente normal

    # Factor 1: hora inusual (madrugada)
    hora = sesion.hora_inicio.hour if sesion.hora_inicio else 14
    if hora < 6:
        score_base += 0.35
        factores.append(f"Acceso en madrugada ({hora:02d}:00h)")
    elif hora > 23:
        score_base += 0.20
        factores.append("Acceso en horario nocturno tardío")

    # Factor 2: IP extranjera (simplificado: rangos no colombianos)
    co_prefixes = ("181.", "190.", "186.", "200.", "181.53", "190.147")
    ip = sesion.ip or ""
    if ip and not any(ip.startswith(p) for p in co_prefixes):
        score_base += 0.30
        factores.append(f"IP no colombiana detectada ({ip})")

    # Factor 3: dispositivo sospechoso
    suspicious_devices = ("curl", "Bot", "Postman", "python-requests", "wget")
    device = sesion.dispositivo or ""
    if any(d.lower() in device.lower() for d in suspicious_devices):
        score_base += 0.30
        factores.append(f"Dispositivo automatizado: {device}")

    # Factor 4: distancia geográfica (si hay coords)
    if sesion.latitud and sesion.longitud and sesion.usuario_id:
        perfil = _get_perfil(sesion.usuario_id)
        if perfil and perfil.ubicacion_habitual:
            dist = _distancia_perfil(
                float(sesion.latitud), float(sesion.longitud), perfil
            )
            if dist > 500:
                score_base += 0.35
                factores.append(f"Acceso a {dist:.0f} km de la ubicación habitual")
            elif dist > 100:
                score_base += 0.15
                factores.append(f"Acceso a {dist:.0f} km de la ubicación habitual")

    # Variación mínima (simula ruido del modelo real)
    puntaje = min(score_base + random.uniform(-0.03, 0.03), 1.0)
    puntaje = round(max(puntaje, 0.0), 4)

    nivel, descripcion, accion = _clasificar(puntaje)
    return {
        "puntaje":     puntaje,
        "nivel":       nivel,
        "descripcion": descripcion if not factores else
                       f"{descripcion} Factores: {'; '.join(factores)}.",
        "factores":    factores,
        "accion":      accion,
    }


# ─── MODELO REAL (Semana 3) ───────────────────────────────────────────────────

def _analizar_con_modelo(sesion) -> dict:
    """
    Carga el Isolation Forest serializado y evalúa la sesión.
    Descomentar en Semana 3 cuando ia/evaluar.py esté implementado.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ia"))
    from evaluar import clasificar_sesion

    perfil = _get_perfil(sesion.usuario_id)
    datos  = {
        "hora":               sesion.hora_inicio.hour if sesion.hora_inicio else 12,
        "dia_semana":         sesion.hora_inicio.weekday() if sesion.hora_inicio else 0,
        "ip":                 sesion.ip,
        "dispositivo":        sesion.dispositivo,
        "latitud":            float(sesion.latitud) if sesion.latitud else None,
        "longitud":           float(sesion.longitud) if sesion.longitud else None,
        "ubicacion_habitual": perfil.ubicacion_habitual if perfil else None,
        "ips_habituales":     perfil.ips_habituales if perfil else [],
        "dispositivos_habituales": perfil.dispositivos_habituales if perfil else [],
        "umbral_monto":       float(perfil.umbral_monto) if perfil else 0,
    }
    return clasificar_sesion(datos)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _clasificar(puntaje: float) -> tuple:
    if puntaje >= UMBRAL_CRITICO:
        return "CRITICO", "Patrón completamente fuera del perfil. Posible suplantación activa.", "bloqueo_definitivo"
    elif puntaje >= UMBRAL_ALTO:
        return "ALTO", "Múltiples factores anómalos detectados. Autenticación reforzada recomendada.", "autenticacion_reforzada"
    elif puntaje >= UMBRAL_MEDIO:
        return "MEDIO", "Acceso con patrón inusual. Requiere monitoreo.", "monitoreo"
    else:
        return "BAJO", "Sesión dentro de parámetros normales.", "ninguna"


def _get_perfil(usuario_id: int):
    from config.database import db
    from models.perfil import PerfilComportamiento
    return PerfilComportamiento.query.filter_by(usuario_id=usuario_id).first()


def _distancia_perfil(lat: float, lon: float, perfil) -> float:
    """Haversine simplificado a coordenadas de la ciudad del perfil."""
    from services.geo_service import CIUDADES_CO
    ciudad = perfil.ubicacion_habitual
    if not ciudad or ciudad not in CIUDADES_CO:
        return 0.0
    lat2, lon2 = CIUDADES_CO[ciudad]
    return _haversine(lat, lon, lat2, lon2)


def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((phi2 - phi1) / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return round(2 * R * math.asin(math.sqrt(a)), 2)
