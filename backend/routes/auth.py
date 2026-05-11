from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config.database import db
from models.usuario  import Usuario
from models.analista import Analista
from models.intento  import IntentoAutenticacion

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login/usuario", methods=["POST"])
def login_usuario():
    """
    UC1 — Login de cliente FinTrust.
    Registra el intento (exitoso o fallido) en intentos_autenticacion.
    Bloquea la cuenta tras MAX_INTENTOS_LOGIN fallos consecutivos.
    Body: { email, password, ip?, dispositivo? }
    """
    data = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    ip       = data.get("ip") or request.remote_addr
    device   = data.get("dispositivo")

    if not email or not password:
        return jsonify({"error": "email y password son requeridos"}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    def _log_intento(exitoso: bool, motivo: str = None):
        intento = IntentoAutenticacion(
            usuario_id   = usuario.id if usuario else 0,
            ip           = ip,
            dispositivo  = device,
            exitoso      = exitoso,
            motivo_fallo = motivo,
        )
        db.session.add(intento)

    if not usuario:
        _log_intento(False, "usuario_no_encontrado")
        db.session.commit()
        return jsonify({"error": "Credenciales inválidas"}), 401

    if usuario.bloqueado:
        _log_intento(False, "cuenta_bloqueada")
        db.session.commit()
        return jsonify({"error": "Cuenta bloqueada. Contacte soporte.", "bloqueado": True}), 403

    if not usuario.check_password(password):
        max_int = current_app.config.get("MAX_INTENTOS_LOGIN", 3)
        # Contar fallos recientes consecutivos
        from sqlalchemy import func
        fallos = (IntentoAutenticacion.query
                  .filter_by(usuario_id=usuario.id, exitoso=False)
                  .order_by(IntentoAutenticacion.fecha.desc())
                  .limit(max_int).count())

        _log_intento(False, "contraseña_incorrecta")

        if fallos + 1 >= max_int:
            usuario.bloqueado      = True
            usuario.motivo_bloqueo = "Múltiples intentos fallidos de autenticación"
            db.session.commit()
            return jsonify({"error": "Cuenta bloqueada por múltiples intentos.", "bloqueado": True}), 403

        db.session.commit()
        return jsonify({"error": "Credenciales inválidas",
                        "intentos_restantes": max_int - fallos - 1}), 401

    # ── Login exitoso ──────────────────────────────────────────────────────────
    usuario.ultimo_acceso = datetime.now(timezone.utc)
    _log_intento(True)
    db.session.commit()

    token = create_access_token(
        identity=f"u:{usuario.id}",
        additional_claims={"tipo": "usuario", "rol": usuario.segmento}
    )
    return jsonify({"access_token": token, "tipo": "usuario", "usuario": usuario.to_dict()}), 200


@auth_bp.route("/login/analista", methods=["POST"])
def login_analista():
    """Login para analistas/supervisores del tablero de seguridad."""
    data     = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email y password son requeridos"}), 400

    analista = Analista.query.filter_by(email=email).first()
    if not analista or not analista.check_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 401
    if not analista.activo:
        return jsonify({"error": "Cuenta desactivada"}), 403

    token = create_access_token(
        identity=f"a:{analista.id}",
        additional_claims={"tipo": "analista", "rol": analista.rol}
    )
    return jsonify({"access_token": token, "tipo": "analista", "analista": analista.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Retorna el perfil del actor autenticado (usuario o analista)."""
    identity = get_jwt_identity()
    if identity.startswith("u:"):
        obj = db.session.get(Usuario, int(identity[2:]))
        return jsonify({"tipo": "usuario", "data": obj.to_dict()}) if obj else (jsonify({"error": "No encontrado"}), 404)
    else:
        obj = db.session.get(Analista, int(identity[2:]))
        return jsonify({"tipo": "analista", "data": obj.to_dict()}) if obj else (jsonify({"error": "No encontrado"}), 404)
