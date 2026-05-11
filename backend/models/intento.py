from datetime import datetime, timezone
from config.database import db


class IntentoAutenticacion(db.Model):
    """
    Tabla: intentos_autenticacion
    Historial de logins exitosos y fallidos.
    Los fallidos NO generan sesión — están separados para rastrear ataques.
    """
    __tablename__ = "intentos_autenticacion"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id    = db.Column(db.Integer, db.ForeignKey("usuarios.id",
                               ondelete="CASCADE", onupdate="CASCADE"),
                              nullable=False, index=True)
    ip            = db.Column(db.String(45), nullable=False, index=True)
    dispositivo   = db.Column(db.String(255), nullable=True)
    exitoso       = db.Column(db.Boolean, nullable=False, default=False)
    motivo_fallo  = db.Column(db.String(120), nullable=True)
    fecha         = db.Column(db.DateTime, nullable=False,
                              default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "usuario_id":   self.usuario_id,
            "ip":           self.ip,
            "dispositivo":  self.dispositivo,
            "exitoso":      self.exitoso,
            "motivo_fallo": self.motivo_fallo,
            "fecha":        self.fecha.isoformat() if self.fecha else None,
        }
