from datetime import datetime, timezone
from config.database import db


class Sesion(db.Model):
    """
    Tabla: sesiones
    Cada acceso exitoso a la plataforma.
    El Motor IA escribe puntaje_anomalia y nivel_riesgo aquí.
    es_anomala: NULL=sin revisar | 1=fraude confirmado | 0=legítima
    """
    __tablename__ = "sesiones"

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id       = db.Column(db.Integer, db.ForeignKey("usuarios.id",
                                  ondelete="CASCADE", onupdate="CASCADE"),
                                 nullable=False, index=True)

    ip               = db.Column(db.String(45), nullable=False)
    dispositivo      = db.Column(db.String(255), nullable=True)
    ubicacion        = db.Column(db.String(100), nullable=True)
    latitud          = db.Column(db.Numeric(9, 6), nullable=True)
    longitud         = db.Column(db.Numeric(9, 6), nullable=True)

    hora_inicio      = db.Column(db.DateTime, nullable=False,
                                 default=lambda: datetime.now(timezone.utc), index=True)
    hora_fin         = db.Column(db.DateTime, nullable=True)

    # Resultado del Isolation Forest (-1.0 a 1.0; más negativo = más anómalo)
    puntaje_anomalia = db.Column(db.Float, nullable=True)
    nivel_riesgo     = db.Column(
                         db.Enum("BAJO", "MEDIO", "ALTO", "CRITICO"),
                         nullable=False, default="BAJO", index=True
                       )
    es_anomala       = db.Column(db.Boolean, nullable=True)   # NULL = sin revisar

    # ── Relaciones ────────────────────────────────────────────────────────────
    transacciones   = db.relationship("Transaccion", backref="sesion",
                                      lazy="dynamic", cascade="all, delete-orphan")
    alertas         = db.relationship("Alerta", backref="sesion",
                                      lazy="dynamic", cascade="all, delete-orphan")
    dato_entrenamiento = db.relationship("DatoEntrenamientoIA", backref="sesion",
                                          uselist=False, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "usuario_id":       self.usuario_id,
            "ip":               self.ip,
            "dispositivo":      self.dispositivo,
            "ubicacion":        self.ubicacion,
            "latitud":          float(self.latitud) if self.latitud else None,
            "longitud":         float(self.longitud) if self.longitud else None,
            "hora_inicio":      self.hora_inicio.isoformat() if self.hora_inicio else None,
            "hora_fin":         self.hora_fin.isoformat() if self.hora_fin else None,
            "puntaje_anomalia": self.puntaje_anomalia,
            "nivel_riesgo":     self.nivel_riesgo,
            "es_anomala":       self.es_anomala,
        }

    def __repr__(self):
        return f"<Sesion {self.id} u={self.usuario_id} [{self.nivel_riesgo}]>"
