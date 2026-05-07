"""
Rutas de autenticación: login, logout, perfil del analista.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from backend.config.database import SessionLocal
from backend.models.usuario import Usuario
import json

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email y contraseña requeridos"}), 400

    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter_by(email=data["email"]).first()
        if not usuario or not check_password_hash(usuario.password_hash, data["password"]):
            return jsonify({"error": "Credenciales inválidas"}), 401

        if usuario.estado == "BLOQUEADA":
            return jsonify({"error": "Cuenta bloqueada. Contacte al administrador."}), 403

        token = create_access_token(
            identity=usuario.id,
            additional_claims={
                "email": usuario.email,
                "rol": usuario.rol,
                "nombre": usuario.nombre,
            }
        )

        return jsonify({
            "access_token": token,
            "usuario": usuario.to_dict()
        }), 200
    finally:
        db.close()


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    identity = get_jwt_identity()
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter_by(id=identity).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(usuario.to_dict()), 200
    finally:
        db.close()
