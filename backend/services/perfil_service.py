"""
Actualiza el perfil de comportamiento tras una sesión normal (BAJO riesgo).
Implementa una media móvil exponencial para ir ajustando los parámetros.
"""
from datetime import datetime, timezone
from config.database import db
from models.perfil   import PerfilComportamiento


def actualizar_perfil(sesion) -> None:
    """
    Llamar al cerrar una sesión con nivel_riesgo == 'BAJO'.
    Actualiza listas de IPs/dispositivos habituales y frecuencia.
    """
    perfil = PerfilComportamiento.query.filter_by(usuario_id=sesion.usuario_id).first()
    if not perfil:
        return

    # ── Actualizar IPs habituales ─────────────────────────────────────────────
    ips = perfil.ips_habituales or []
    if sesion.ip and sesion.ip not in ips:
        ips.append(sesion.ip)
        perfil.ips_habituales = ips[-5:]    # máximo 5 IPs habituales

    # ── Actualizar dispositivos habituales ────────────────────────────────────
    devs = perfil.dispositivos_habituales or []
    if sesion.dispositivo and sesion.dispositivo not in devs:
        devs.append(sesion.dispositivo)
        perfil.dispositivos_habituales = devs[-5:]

    perfil.ultima_actualizacion = datetime.now(timezone.utc)
    # No hacemos commit aquí — el caller maneja la transacción
