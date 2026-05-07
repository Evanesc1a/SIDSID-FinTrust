import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from backend.config.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    estado = Column(String, default="ACTIVA")  # ACTIVA, BLOQUEADA, SUSPENDIDA
    rol = Column(String, default="usuario")    # usuario, analista, admin
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "estado": self.estado,
            "rol": self.rol,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
        }
