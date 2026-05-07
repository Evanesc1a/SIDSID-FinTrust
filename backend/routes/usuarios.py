"""
Rutas para gestión de usuarios.
"""
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash

from backend.config.database import SessionLocal
from backend.models.usuario import Usuario
from backend.services.perfil_service import obtener_o_crear_perfil

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@usuarios_bp.route("", methods=["GET"])
@jwt_required()
def listar_usuarios():
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
        return jsonify([u.to_dict() for u in usuarios]), 200
    finally:
        db.close()


@usuarios_bp.route("/<usuario_id>", methods=["GET"])
@jwt_required()
def obtener_usuario(usuario_id):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(usuario.to_dict()), 200
    finally:
        db.close()


@usuarios_bp.route("/<usuario_id>/perfil", methods=["GET"])
@jwt_required()
def obtener_perfil(usuario_id):
    db = SessionLocal()
    try:
        perfil = obtener_o_crear_perfil(db, usuario_id)
        return jsonify(perfil.to_dict()), 200
    finally:
        db.close()


@usuarios_bp.route("/<usuario_id>/bloquear", methods=["POST"])
@jwt_required()
def bloquear_usuario(usuario_id):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        usuario.estado = "BLOQUEADA"
        db.commit()
        return jsonify({"mensaje": f"Usuario {usuario.nombre} bloqueado.", "usuario": usuario.to_dict()}), 200
    finally:
        db.close()


@usuarios_bp.route("/<usuario_id>/desbloquear", methods=["POST"])
@jwt_required()
def desbloquear_usuario(usuario_id):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        usuario.estado = "ACTIVA"
        db.commit()
        return jsonify({"mensaje": f"Usuario {usuario.nombre} desbloqueado.", "usuario": usuario.to_dict()}), 200
    finally:
        db.close()
