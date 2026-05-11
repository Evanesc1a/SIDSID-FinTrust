from datetime import datetime, timezone
from config.database import db


class PerfilComportamiento(db.Model):
    """
    Tabla: perfiles_comportamiento
    Línea base del comportamiento normal de cada usuario.
    Relación 1-a-1 con usuarios.
    """
    __tablename__ = "perfiles_comportamiento"

    id                     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id             = db.Column(db.Integer, db.ForeignKey("usuarios.id",
                                        ondelete="CASCADE", onupdate="CASCADE"),
                                       nullable=False, unique=True, index=True)

    dispositivos_habituales = db.Column(db.JSON, nullable=True)
    ips_habituales          = db.Column(db.JSON, nullable=True)
    horario_tipico          = db.Column(db.String(15), nullable=True)  # "HH:MM-HH:MM"
    umbral_monto            = db.Column(db.Numeric(14, 2), nullable=False, default=0.00)
    ubicacion_habitual      = db.Column(db.String(100), nullable=True)
    frecuencia_semanal_avg  = db.Column(db.Float, nullable=True)
    ultima_actualizacion    = db.Column(db.DateTime, nullable=False,
                                        default=lambda: datetime.now(timezone.utc),
                                        onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id":                      self.id,
            "usuario_id":              self.usuario_id,
            "dispositivos_habituales": self.dispositivos_habituales or [],
            "ips_habituales":          self.ips_habituales or [],
            "horario_tipico":          self.horario_tipico,
            "umbral_monto":            float(self.umbral_monto or 0),
            "ubicacion_habitual":      self.ubicacion_habitual,
            "frecuencia_semanal_avg":  self.frecuencia_semanal_avg,
            "ultima_actualizacion":    self.ultima_actualizacion.isoformat()
                                       if self.ultima_actualizacion else None,
        }
