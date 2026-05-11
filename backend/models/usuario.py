from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from config.database import db


class Usuario(db.Model):
    """
    Tabla: usuarios
    Clientes finales de la plataforma FinTrust.
    """
    __tablename__ = "usuarios"

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email           = db.Column(db.String(180), nullable=False, unique=True, index=True)
    nombre          = db.Column(db.String(120), nullable=False)
    hash_password   = db.Column(db.String(255), nullable=False)
    telefono        = db.Column(db.String(20), nullable=True)
    segmento        = db.Column(
                        db.Enum("no_bancarizado", "bancarizado", "pyme"),
                        nullable=False, default="no_bancarizado"
                      )
    bloqueado       = db.Column(db.Boolean, nullable=False, default=False, index=True)
    motivo_bloqueo  = db.Column(db.String(255), nullable=True)
    fecha_creacion  = db.Column(db.DateTime, nullable=False,
                                default=lambda: datetime.now(timezone.utc))
    ultimo_acceso   = db.Column(db.DateTime, nullable=True)

    # ── Relaciones ────────────────────────────────────────────────────────────
    perfil   = db.relationship("PerfilComportamiento", backref="usuario",
                                uselist=False, cascade="all, delete-orphan")
    sesiones = db.relationship("Sesion", backref="usuario", lazy="dynamic",
                                cascade="all, delete-orphan",
                                foreign_keys="Sesion.usuario_id")
    intentos = db.relationship("IntentoAutenticacion", backref="usuario",
                                lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, pwd: str):
        self.hash_password = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self.hash_password, pwd)

    def to_dict(self, include_sensitive=False) -> dict:
        data = {
            "id":             self.id,
            "email":          self.email,
            "nombre":         self.nombre,
            "telefono":       self.telefono,
            "segmento":       self.segmento,
            "bloqueado":      self.bloqueado,
            "motivo_bloqueo": self.motivo_bloqueo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "ultimo_acceso":  self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
        }
        return data

    def __repr__(self):
        return f"<Usuario {self.email} [{self.segmento}]>"
