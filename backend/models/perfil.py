import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Text
from backend.config.database import Base

class PerfilComportamiento(Base):
    __tablename__ = "perfiles_comportamiento"

    usuario_id = Column(String, primary_key=True)
    dispositivos_frecuentes = Column(Text, default="[]")   # JSON list
    horarios_habituales = Column(Text, default="[]")        # JSON list
    ubicaciones_habituales = Column(Text, default="[]")     # JSON list
    ips_habituales = Column(Text, default="[]")             # JSON list
    frecuencia_tx = Column(Float, default=0.0)
    monto_promedio_tx = Column(Float, default=0.0)
    sesiones_promedio_dia = Column(Float, default=1.0)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "usuario_id": self.usuario_id,
            "dispositivos_frecuentes": json.loads(self.dispositivos_frecuentes or "[]"),
            "horarios_habituales": json.loads(self.horarios_habituales or "[]"),
            "ubicaciones_habituales": json.loads(self.ubicaciones_habituales or "[]"),
            "ips_habituales": json.loads(self.ips_habituales or "[]"),
            "frecuencia_tx": self.frecuencia_tx,
            "monto_promedio_tx": self.monto_promedio_tx,
            "sesiones_promedio_dia": self.sesiones_promedio_dia,
            "ultima_actualizacion": self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None,
        }
