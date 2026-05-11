from routes.auth      import auth_bp
from routes.sesiones  import sesiones_bp
from routes.alertas   import alertas_bp
from routes.usuarios  import usuarios_bp
from routes.analistas import analistas_bp
from routes.metricas  import metricas_bp
from routes.analisis  import analisis_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp,      url_prefix="/auth")
    app.register_blueprint(sesiones_bp,  url_prefix="/sesiones")
    app.register_blueprint(alertas_bp,   url_prefix="/alertas")
    app.register_blueprint(usuarios_bp,  url_prefix="/usuarios")
    app.register_blueprint(analistas_bp, url_prefix="/analistas")
    app.register_blueprint(metricas_bp,  url_prefix="/metricas")
    app.register_blueprint(analisis_bp,  url_prefix="/api")
