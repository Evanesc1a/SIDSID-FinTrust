from datetime import datetime, timezone
from config.database import db


class Alerta(db.Model):
    """
    Tabla: alertas
    Generadas por el Motor IA; gestionadas por el Analista en el tablero.
    """
    __tablename__ = "alertas"

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sesion_id         = db.Column(db.Integer, db.ForeignKey("sesiones.id",
                                   ondelete="CASCADE", onupdate="CASCADE"),
                                  nullable=False, index=True)
    analista_id       = db.Column(db.Integer, db.ForeignKey("analistas.id",
                                   ondelete="SET NULL", onupdate="CASCADE"),
                                  nullable=True, index=True)

    nivel_riesgo      = db.Column(
                          db.Enum("MEDIO", "ALTO", "CRITICO"),
                          nullable=False, index=True
                        )
    descripcion       = db.Column(db.Text, nullable=True)
    resuelta          = db.Column(db.Boolean, nullable=False, default=False, index=True)

    decision_analista = db.Column(
                          db.Enum("PENDIENTE", "CONFIRMADO_FRAUDE",
                                  "FALSO_POSITIVO", "REQUIERE_MAS_INFO"),
                          nullable=False, default="PENDIENTE"
                        )
    motivo_descarte   = db.Column(db.String(255), nullable=True)
    accion_tomada     = db.Column(
                          db.Enum("ninguna", "autenticacion_reforzada",
                                  "bloqueo_preventivo", "bloqueo_definitivo",
                                  "reversion_transacciones"),
                          nullable=False, default="ninguna"
                        )

    fecha_generacion  = db.Column(db.DateTime, nullable=False,
                                  default=lambda: datetime.now(timezone.utc), index=True)
    fecha_resolucion  = db.Column(db.DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "sesion_id":         self.sesion_id,
            "analista_id":       self.analista_id,
            "nivel_riesgo":      self.nivel_riesgo,
            "descripcion":       self.descripcion,
            "resuelta":          self.resuelta,
            "decision_analista": self.decision_analista,
            "motivo_descarte":   self.motivo_descarte,
            "accion_tomada":     self.accion_tomada,
            "fecha_generacion":  self.fecha_generacion.isoformat() if self.fecha_generacion else None,
            "fecha_resolucion":  self.fecha_resolucion.isoformat() if self.fecha_resolucion else None,
        }

    def __repr__(self):
        return f"<Alerta {self.id} [{self.nivel_riesgo}] resuelta={self.resuelta}>"
