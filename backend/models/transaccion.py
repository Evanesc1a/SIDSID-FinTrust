from datetime import datetime, timezone
from config.database import db


class Transaccion(db.Model):
    """Tabla: transacciones — movimientos financieros dentro de una sesión."""
    __tablename__ = "transacciones"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sesion_id     = db.Column(db.Integer, db.ForeignKey("sesiones.id",
                               ondelete="CASCADE", onupdate="CASCADE"),
                              nullable=False, index=True)
    tipo          = db.Column(
                     db.Enum("pago", "transferencia", "recarga", "retiro", "credito"),
                     nullable=False
                   )
    monto         = db.Column(db.Numeric(14, 2), nullable=False)
    estado        = db.Column(
                     db.Enum("pendiente", "completada", "fallida", "revertida"),
                     nullable=False, default="pendiente"
                   )
    es_sospechosa = db.Column(db.Boolean, nullable=False, default=False)
    descripcion   = db.Column(db.String(255), nullable=True)
    hora          = db.Column(db.DateTime, nullable=False,
                              default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "sesion_id":     self.sesion_id,
            "tipo":          self.tipo,
            "monto":         float(self.monto),
            "estado":        self.estado,
            "es_sospechosa": self.es_sospechosa,
            "descripcion":   self.descripcion,
            "hora":          self.hora.isoformat() if self.hora else None,
        }
