import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, Text
from backend.config.database import Base

class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, nullable=False)
    fecha_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    dispositivo_id = Column(String)
    ubicacion = Column(String)
    ip_acceso = Column(String)
    duracion_min = Column(Integer, default=0)
    tipo_acceso = Column(String, default="web")  # web, mobile, api
    # Campos IA
    puntaje_anomalia = Column(Float, default=0.0)
    es_anomala = Column(Integer, default=0)  # 0=normal, 1=anomala
    nivel_riesgo = Column(String, default="BAJO")

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
            "dispositivo_id": self.dispositivo_id,
            "ubicacion": self.ubicacion,
            "ip_acceso": self.ip_acceso,
            "duracion_min": self.duracion_min,
            "tipo_acceso": self.tipo_acceso,
            "puntaje_anomalia": self.puntaje_anomalia,
            "es_anomala": self.es_anomala,
            "nivel_riesgo": self.nivel_riesgo,
        }
