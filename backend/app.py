"""
app.py — Punto de entrada de la API SIDSID / FinTrust
======================================================
Ejecutar en desarrollo:
    cd backend
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    flask db init && flask db migrate -m "init" && flask db upgrade
    python scripts/seed_data.py          # poblar la BD
    flask run --reload
"""
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config.settings  import get_config
from config.database  import init_db


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(get_config())
    if config_override:
        app.config.update(config_override)

    # ── Extensiones ───────────────────────────────────────────────────────────
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    JWTManager(app)
    init_db(app)

    # ── Importar modelos para que Flask-Migrate los detecte ───────────────────
    with app.app_context():
        import models  # noqa — registra todos los modelos

    # ── Blueprints ────────────────────────────────────────────────────────────
    from routes import register_blueprints
    register_blueprints(app)

    # ── Health-check ──────────────────────────────────────────────────────────
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "servicio": "SIDSID-API"}), 200

    # ── Manejadores de error globales ─────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Método no permitido"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Error interno del servidor"}), 500

    return app


# ── Entry point ───────────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
