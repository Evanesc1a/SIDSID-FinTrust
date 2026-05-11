from datetime import datetime, timezone
from config.database import db


class MetricaModelo(db.Model):
    """
    Tabla: metricas_modelo
    Historial de evaluaciones del modelo IA (KPIs para la junta directiva).
    """
    __tablename__ = "metricas_modelo"

    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version_modelo          = db.Column(db.String(50), nullable=False, index=True)
    contaminacion           = db.Column(db.Float, nullable=False)
    n_estimadores           = db.Column(db.SmallInteger, nullable=False)

    precision_score         = db.Column(db.Float, nullable=True)
    recall_score            = db.Column(db.Float, nullable=True)
    f1_score                = db.Column(db.Float, nullable=True)
    tasa_falsos_positivos   = db.Column(db.Float, nullable=True)
    tasa_deteccion_temprana = db.Column(db.Float, nullable=True)

    total_sesiones          = db.Column(db.Integer, nullable=False, default=0)
    total_alertas           = db.Column(db.Integer, nullable=False, default=0)
    alertas_confirmadas     = db.Column(db.Integer, nullable=False, default=0)
    alertas_descartadas     = db.Column(db.Integer, nullable=False, default=0)
    tiempo_respuesta_avg_min= db.Column(db.Float, nullable=True)
    notas                   = db.Column(db.Text, nullable=True)
    fecha_evaluacion        = db.Column(db.DateTime, nullable=False,
                                        default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self) -> dict:
        return {
            "id":                       self.id,
            "version_modelo":           self.version_modelo,
            "contaminacion":            self.contaminacion,
            "n_estimadores":            self.n_estimadores,
            "precision_score":          self.precision_score,
            "recall_score":             self.recall_score,
            "f1_score":                 self.f1_score,
            "tasa_falsos_positivos":    self.tasa_falsos_positivos,
            "tasa_deteccion_temprana":  self.tasa_deteccion_temprana,
            "total_sesiones":           self.total_sesiones,
            "total_alertas":            self.total_alertas,
            "alertas_confirmadas":      self.alertas_confirmadas,
            "alertas_descartadas":      self.alertas_descartadas,
            "tiempo_respuesta_avg_min": self.tiempo_respuesta_avg_min,
            "notas":                    self.notas,
            "fecha_evaluacion":         self.fecha_evaluacion.isoformat() if self.fecha_evaluacion else None,
        }
