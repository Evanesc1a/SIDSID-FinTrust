from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from config.database import db


class Analista(db.Model):
    """
    Tabla: analistas
    Operadores del tablero de seguridad (analista / supervisor / admin).
    """
    __tablename__ = "analistas"

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre         = db.Column(db.String(120), nullable=False)
    email          = db.Column(db.String(180), nullable=False, unique=True, index=True)
    hash_password  = db.Column(db.String(255), nullable=False)
    rol            = db.Column(db.Enum("analista", "supervisor", "admin"),
                               nullable=False, default="analista")
    activo         = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False,
                               default=lambda: datetime.now(timezone.utc))

    # Relación inversa con alertas
    alertas = db.relationship("Alerta", backref="analista", lazy="dynamic",
                               foreign_keys="Alerta.analista_id")

    def set_password(self, pwd: str):
        self.hash_password = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self.hash_password, pwd)

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "nombre":         self.nombre,
            "email":          self.email,
            "rol":            self.rol,
            "activo":         self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }

    def __repr__(self):
        return f"<Analista {self.email} [{self.rol}]>"
