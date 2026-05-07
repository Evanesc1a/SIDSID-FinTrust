"""
SIDSID — Sistema Inteligente de Detección de Suplantación de Identidad Digital
FinTrust Digital Services S.A.S.

Punto de entrada principal de la aplicación Flask.
"""
import os
import sys

# Agregar directorio raíz al path para imports del módulo IA
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(ROOT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from backend.config.settings import Config
from backend.config.database import init_db
from backend.routes import auth_bp, sesiones_bp, alertas_bp, usuarios_bp, metricas_bp, analisis_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    CORS(app,
         origins=["http://localhost:3000", "http://localhost:5173"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    JWTManager(app)

    # Initialize DB
    init_db()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(sesiones_bp)
    app.register_blueprint(alertas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(metricas_bp)
    app.register_blueprint(analisis_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "sistema": "SIDSID", "version": "1.0"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint no encontrado"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Error interno del servidor"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
