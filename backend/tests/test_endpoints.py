"""
Tests de endpoints del backend SIDSID.
Ejecutar con: python -m pytest backend/tests/test_endpoints.py -v
"""
import sys
import os
import uuid
import pytest
from werkzeug.security import generate_password_hash

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

# Forzar BD en memoria para pruebas — ANTES de importar la app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from backend.app import create_app
from backend.config.database import SessionLocal, Base, engine
from backend.models.usuario import Usuario
from backend.models.perfil import PerfilComportamiento


def _seed_test_db():
    """Puebla la BD de prueba con datos mínimos necesarios."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        analista_id = str(uuid.uuid4())
        usuario_id = str(uuid.uuid4())

        analista = Usuario(
            id=analista_id,
            nombre="Analista Test",
            email="analista@fintrust.co",
            password_hash=generate_password_hash("sidsid123"),
            rol="analista",
            estado="ACTIVA",
        )
        usuario = Usuario(
            id=usuario_id,
            nombre="Usuario Test",
            email="usuario1@fintrust.co",
            password_hash=generate_password_hash("user123"),
            rol="usuario",
            estado="ACTIVA",
        )
        perfil = PerfilComportamiento(
            usuario_id=usuario_id,
            dispositivos_frecuentes='["iPhone-14"]',
            ubicaciones_habituales='["Bogotá"]',
            ips_habituales='["192.168.1.10"]',
            monto_promedio_tx=100000.0,
            frecuencia_tx=2.0,
            sesiones_promedio_dia=1.0,
        )
        db.add_all([analista, usuario, perfil])
        db.commit()
        return analista_id, usuario_id
    finally:
        db.close()


@pytest.fixture(scope="session")
def app():
    application = create_app()
    application.config["TESTING"] = True
    _seed_test_db()
    return application


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def token(client):
    res = client.post("/api/auth/login", json={
        "email": "analista@fintrust.co",
        "password": "sidsid123",
    })
    assert res.status_code == 200, f"Login fallido: {res.get_json()}"
    return res.get_json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ─── Health ───────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "ok"
        assert data["sistema"] == "SIDSID"


# ─── Auth ─────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_login_valido(self, client):
        res = client.post("/api/auth/login", json={
            "email": "analista@fintrust.co",
            "password": "sidsid123",
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "access_token" in data
        assert "usuario" in data

    def test_login_invalido(self, client):
        res = client.post("/api/auth/login", json={
            "email": "noexiste@fintrust.co",
            "password": "wrong",
        })
        assert res.status_code == 401

    def test_login_sin_datos(self, client):
        res = client.post("/api/auth/login", json={})
        assert res.status_code == 400

    def test_me_autenticado(self, client, token):
        res = client.get("/api/auth/me", headers=auth(token))
        assert res.status_code == 200
        data = res.get_json()
        assert "email" in data

    def test_me_sin_token(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 401


# ─── Usuarios ─────────────────────────────────────────────────────────────────

class TestUsuarios:
    def test_listar_usuarios(self, client, token):
        res = client.get("/api/usuarios", headers=auth(token))
        assert res.status_code == 200
        usuarios = res.get_json()
        assert isinstance(usuarios, list)
        assert len(usuarios) >= 2

    def test_obtener_usuario_existente(self, client, token):
        usuarios = client.get("/api/usuarios", headers=auth(token)).get_json()
        uid = usuarios[0]["id"]
        res = client.get(f"/api/usuarios/{uid}", headers=auth(token))
        assert res.status_code == 200

    def test_obtener_usuario_inexistente(self, client, token):
        res = client.get("/api/usuarios/id-que-no-existe", headers=auth(token))
        assert res.status_code == 404

    def test_listar_usuarios_sin_token(self, client):
        res = client.get("/api/usuarios")
        assert res.status_code == 401


# ─── Alertas ──────────────────────────────────────────────────────────────────

class TestAlertas:
    def test_listar_alertas(self, client, token):
        res = client.get("/api/alertas", headers=auth(token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_resumen_alertas(self, client, token):
        res = client.get("/api/alertas/resumen", headers=auth(token))
        assert res.status_code == 200
        data = res.get_json()
        assert "por_nivel" in data
        assert "total_nuevas" in data
        for nivel in ["BAJO", "MEDIO", "ALTO", "CRITICO"]:
            assert nivel in data["por_nivel"]

    def test_alertas_sin_token(self, client):
        res = client.get("/api/alertas")
        assert res.status_code == 401

    def test_alerta_inexistente(self, client, token):
        res = client.get("/api/alertas/id-que-no-existe", headers=auth(token))
        assert res.status_code == 404


# ─── Métricas ─────────────────────────────────────────────────────────────────

class TestMetricas:
    def test_metricas_sistema(self, client, token):
        res = client.get("/api/metricas", headers=auth(token))
        assert res.status_code == 200
        data = res.get_json()
        assert "sesiones" in data
        assert "alertas" in data
        assert "usuarios" in data
        assert "tendencia_anomalias" in data
        assert "modelo_ia" in data
        assert len(data["tendencia_anomalias"]) == 7

    def test_metricas_estructura_sesiones(self, client, token):
        data = client.get("/api/metricas", headers=auth(token)).get_json()
        s = data["sesiones"]
        assert "total_24h" in s
        assert "anomalas_24h" in s
        assert "tasa_anomalia" in s

    def test_metricas_estructura_alertas(self, client, token):
        data = client.get("/api/metricas", headers=auth(token)).get_json()
        a = data["alertas"]
        assert "nuevas" in a
        assert "criticas" in a
        assert "distribucion_nivel" in a
        for nivel in ["BAJO", "MEDIO", "ALTO", "CRITICO"]:
            assert nivel in a["distribucion_nivel"]

    def test_metricas_sin_token(self, client):
        res = client.get("/api/metricas")
        assert res.status_code == 401


# ─── Sesiones ─────────────────────────────────────────────────────────────────

class TestSesiones:
    def _get_usuario_id(self, client, token):
        usuarios = client.get("/api/usuarios", headers=auth(token)).get_json()
        return next((u["id"] for u in usuarios if u["rol"] == "usuario"), None)

    def test_registrar_sesion_normal(self, client, token):
        uid = self._get_usuario_id(client, token)
        assert uid, "No se encontró usuario de prueba"
        res = client.post("/api/sesiones", headers=auth(token), json={
            "usuario_id": uid,
            "dispositivo_id": "iPhone-14",
            "ubicacion": "Bogotá",
            "ip_acceso": "192.168.1.10",
            "tipo_acceso": "web",
            "monto_sesion": 80000,
            "num_transacciones": 1,
        })
        assert res.status_code == 201
        data = res.get_json()
        assert "sesion" in data
        assert "analisis" in data
        assert data["analisis"]["nivel_riesgo"] in ["BAJO", "MEDIO", "ALTO", "CRITICO"]

    def test_registrar_sesion_anomala(self, client, token):
        uid = self._get_usuario_id(client, token)
        assert uid
        res = client.post("/api/sesiones", headers=auth(token), json={
            "usuario_id": uid,
            "dispositivo_id": "Dispositivo-Extraño-XYZ",
            "ubicacion": "País desconocido",
            "ip_acceso": "91.195.240.117",
            "tipo_acceso": "web",
            "monto_sesion": 5000000,
            "num_transacciones": 25,
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data["analisis"]["nivel_riesgo"] in ["BAJO", "MEDIO", "ALTO", "CRITICO"]

    def test_registrar_sesion_sin_usuario_id(self, client, token):
        res = client.post("/api/sesiones", headers=auth(token), json={
            "dispositivo_id": "iPhone",
        })
        assert res.status_code == 400

    def test_listar_sesiones(self, client, token):
        res = client.get("/api/sesiones", headers=auth(token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_sesion_anomala_crea_alerta(self, client, token):
        uid = self._get_usuario_id(client, token)
        res = client.post("/api/sesiones", headers=auth(token), json={
            "usuario_id": uid,
            "dispositivo_id": "Hacker-Device-99",
            "ubicacion": "Rusia",
            "ip_acceso": "45.33.32.156",
            "tipo_acceso": "web",
            "monto_sesion": 9000000,
            "num_transacciones": 30,
        })
        assert res.status_code == 201
        data = res.get_json()
        if data["analisis"]["nivel_riesgo"] in ["MEDIO", "ALTO", "CRITICO"]:
            assert data["alerta_creada"] is not None
            assert "id" in data["alerta_creada"]


# ─── Análisis IA ──────────────────────────────────────────────────────────────

class TestAnalisisIA:
    def test_analizar_sesion(self, client, token):
        usuarios = client.get("/api/usuarios", headers=auth(token)).get_json()
        uid = next((u["id"] for u in usuarios if u["rol"] == "usuario"), None)
        assert uid
        res = client.post("/api/analizar", headers=auth(token), json={
            "usuario_id": uid,
            "dispositivo_id": "Nuevo-Dispositivo-Sospechoso",
            "ubicacion": "Ciudad desconocida",
            "ip_acceso": "45.33.32.156",
            "monto_sesion": 2000000,
            "num_transacciones": 15,
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "nivel_riesgo" in data
        assert data["nivel_riesgo"] in ["BAJO", "MEDIO", "ALTO", "CRITICO"]
        assert "puntaje" in data
        assert "es_anomala" in data
        assert "factores" in data

    def test_analizar_sin_usuario_id(self, client, token):
        res = client.post("/api/analizar", headers=auth(token), json={
            "dispositivo_id": "iPhone",
        })
        assert res.status_code == 400
