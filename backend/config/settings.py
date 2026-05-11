import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY  = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG       = False
    TESTING     = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/fintrust?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    JWT_SECRET_KEY           = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600)))
    CORS_ORIGINS             = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    MAX_INTENTOS_LOGIN   = int(os.getenv("MAX_INTENTOS_LOGIN", 3))
    UMBRAL_RIESGO_MEDIO  = float(os.getenv("UMBRAL_RIESGO_MEDIO", 0.30))
    UMBRAL_RIESGO_ALTO   = float(os.getenv("UMBRAL_RIESGO_ALTO", 0.55))
    UMBRAL_RIESGO_CRITICO= float(os.getenv("UMBRAL_RIESGO_CRITICO", 0.80))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(Config):
    DEBUG = False

config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}

def get_config():
    return config_map.get(os.getenv("FLASK_ENV", "development"), DevelopmentConfig)
