from datetime import datetime, timezone
from config.database import db


class DatoEntrenamientoIA(db.Model):
    """
    Tabla: datos_entrenamiento_ia
    Vectores de features pre-calculados para entrenar Isolation Forest.
    etiqueta_fraude se actualiza cuando el analista cierra la alerta.
    """
    __tablename__ = "datos_entrenamiento_ia"

    id                        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sesion_id                 = db.Column(db.Integer, db.ForeignKey("sesiones.id",
                                           ondelete="CASCADE", onupdate="CASCADE"),
                                          nullable=False, unique=True)

    # Features de tiempo
    hora_normalizada          = db.Column(db.Float, nullable=False)   # 0.0–1.0
    dia_semana                = db.Column(db.SmallInteger, nullable=False)  # 0=lun..6=dom

    # Features de frecuencia
    frecuencia_acceso_7d      = db.Column(db.SmallInteger, nullable=False, default=0)
    intentos_fallidos_24h     = db.Column(db.SmallInteger, nullable=False, default=0)

    # Features de dispositivo/red
    dispositivo_conocido      = db.Column(db.Boolean, nullable=False, default=False)
    ip_conocida               = db.Column(db.Boolean, nullable=False, default=False)
    distancia_geo_km          = db.Column(db.Float, nullable=False, default=0.0)

    # Features transaccionales
    monto_promedio_historico  = db.Column(db.Numeric(14, 2), nullable=False, default=0.00)
    num_transacciones_sesion  = db.Column(db.SmallInteger, nullable=False, default=0)
    monto_maximo_sesion       = db.Column(db.Numeric(14, 2), nullable=False, default=0.00)

    # Salida del modelo
    puntaje_asignado          = db.Column(db.Float, nullable=True)

    # Etiqueta supervisada (se rellena post-revisión del analista)
    etiqueta_fraude           = db.Column(db.Boolean, nullable=True, index=True)

    fecha_registro            = db.Column(db.DateTime, nullable=False,
                                          default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self) -> dict:
        return {
            "id":                       self.id,
            "sesion_id":                self.sesion_id,
            "hora_normalizada":         self.hora_normalizada,
            "dia_semana":               self.dia_semana,
            "frecuencia_acceso_7d":     self.frecuencia_acceso_7d,
            "intentos_fallidos_24h":    self.intentos_fallidos_24h,
            "dispositivo_conocido":     self.dispositivo_conocido,
            "ip_conocida":              self.ip_conocida,
            "distancia_geo_km":         self.distancia_geo_km,
            "monto_promedio_historico": float(self.monto_promedio_historico or 0),
            "num_transacciones_sesion": self.num_transacciones_sesion,
            "monto_maximo_sesion":      float(self.monto_maximo_sesion or 0),
            "puntaje_asignado":         self.puntaje_asignado,
            "etiqueta_fraude":          self.etiqueta_fraude,
            "fecha_registro":           self.fecha_registro.isoformat() if self.fecha_registro else None,
        }
