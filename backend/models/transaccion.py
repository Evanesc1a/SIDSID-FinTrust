import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Text
from backend.config.database import Base

class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, nullable=False)
    sesion_id = Column(String)
    monto = Column(Float, nullable=False)
    tipo = Column(String)   # PAGO, TRANSFERENCIA, RETIRO, RECARGA
    estado = Column(String, default="COMPLETADA")  # COMPLETADA, PENDIENTE, FALLIDA
    fecha_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    dispositivo = Column(String)
    descripcion = Column(Text)

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "sesion_id": self.sesion_id,
            "monto": self.monto,
            "tipo": self.tipo,
            "estado": self.estado,
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
            "dispositivo": self.dispositivo,
            "descripcion": self.descripcion,
        }
