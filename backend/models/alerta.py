import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float
from backend.config.database import Base

class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, nullable=False)
    sesion_id = Column(String)
    nivel_riesgo = Column(String, nullable=False)  # BAJO, MEDIO, ALTO, CRITICO
    descripcion = Column(Text)
    factores = Column(Text, default="[]")           # JSON list of contributing factors
    puntaje = Column(Float, default=0.0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    estado = Column(String, default="NUEVA")        # NUEVA, REVISADA, RESUELTA, DESCARTADA
    analista_id = Column(String)
    fecha_resolucion = Column(DateTime)
    notas_analista = Column(Text)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "sesion_id": self.sesion_id,
            "nivel_riesgo": self.nivel_riesgo,
            "descripcion": self.descripcion,
            "factores": json.loads(self.factores or "[]"),
            "puntaje": self.puntaje,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "estado": self.estado,
            "analista_id": self.analista_id,
            "fecha_resolucion": self.fecha_resolucion.isoformat() if self.fecha_resolucion else None,
            "notas_analista": self.notas_analista,
        }
