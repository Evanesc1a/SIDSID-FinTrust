"""
Lógica de negocio para generación y actualización de alertas.
Desacoplado del route para facilitar pruebas.
"""
from config.database import db
from models.alerta   import Alerta


def crear_alerta(sesion_id: int, nivel: str, descripcion: str) -> Alerta:
    """Crea y persiste una alerta. No hace commit (el caller lo maneja)."""
    alerta = Alerta(
        sesion_id    = sesion_id,
        nivel_riesgo = nivel,
        descripcion  = descripcion,
    )
    db.session.add(alerta)
    return alerta


def alertas_sin_resolver() -> int:
    return Alerta.query.filter_by(resuelta=False).count()
