"""
Fixtures de pytest para tests del backend SIDSID.
Usa SQLite en memoria → no requiere MySQL para correr los tests.
"""
import pytest
from app import create_app
from config.database import db as _db


@pytest.fixture(scope="session")
def app():
    """App Flask configurada para testing (SQLite en memoria)."""
    _app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
        "WTF_CSRF_ENABLED": False,
    })
    with _app.app_context():
        _db.create_all()
        _seed_test_data()
        yield _app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def token_analista(client):
    """Retorna un JWT válido para el analista de prueba."""
    resp = client.post("/auth/login/analista",
                       json={"email": "test.analista@fintrust.com", "password": "Test1234!"})
    return resp.get_json()["access_token"]


@pytest.fixture()
def token_usuario(client):
    """Retorna un JWT válido para el usuario de prueba."""
    resp = client.post("/auth/login/usuario",
                       json={"email": "test.usuario@example.com", "password": "Test1234!"})
    return resp.get_json()["access_token"]


def _seed_test_data():
    """Inserta datos mínimos para los tests."""
    from models.analista import Analista
    from models.usuario  import Usuario
    from models.perfil   import PerfilComportamiento

    analista = Analista(nombre="Test Analista", email="test.analista@fintrust.com", rol="analista")
    analista.set_password("Test1234!")
    _db.session.add(analista)

    usuario = Usuario(nombre="Test Usuario", email="test.usuario@example.com", segmento="bancarizado")
    usuario.set_password("Test1234!")
    _db.session.add(usuario)
    _db.session.flush()

    perfil = PerfilComportamiento(
        usuario_id=usuario.id,
        ips_habituales=["190.25.1.1"],
        dispositivos_habituales=["Android-Chrome/120"],
        horario_tipico="08:00-22:00",
        umbral_monto=500000,
        ubicacion_habitual="Bogotá",
    )
    _db.session.add(perfil)
    _db.session.commit()
