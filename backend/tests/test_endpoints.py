"""
Tests de endpoints del backend SIDSID.
Ejecutar con: python -m pytest backend/tests/test_endpoints.py -v
"""
import sys
import os
import json
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from backend.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def token(client):
    """Obtiene token JWT de analista para los tests."""
    res = client.post('/api/auth/login', json={
        'email': 'analista@fintrust.co',
        'password': 'sidsid123'
    })
    if res.status_code == 200:
        return res.get_json()['access_token']
    return None


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


class TestHealth:
    def test_health(self, client):
        res = client.get('/api/health')
        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'ok'
        assert data['sistema'] == 'SIDSID'


class TestAuth:
    def test_login_valido(self, client):
        res = client.post('/api/auth/login', json={
            'email': 'analista@fintrust.co',
            'password': 'sidsid123'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert 'access_token' in data
        assert 'usuario' in data

    def test_login_invalido(self, client):
        res = client.post('/api/auth/login', json={
            'email': 'noexiste@fintrust.co',
            'password': 'wrong'
        })
        assert res.status_code == 401

    def test_login_sin_datos(self, client):
        res = client.post('/api/auth/login', json={})
        assert res.status_code == 400

    def test_me_autenticado(self, client, token):
        if not token:
            pytest.skip("No se pudo obtener token")
        res = client.get('/api/auth/me', headers=auth_headers(token))
        assert res.status_code == 200

    def test_me_sin_token(self, client):
        res = client.get('/api/auth/me')
        assert res.status_code == 401


class TestAlertas:
    def test_listar_alertas(self, client, token):
        if not token:
            pytest.skip("No se pudo obtener token")
        res = client.get('/api/alertas', headers=auth_headers(token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_resumen_alertas(self, client, token):
        if not token:
            pytest.skip("No se pudo obtener token")
        res = client.get('/api/alertas/resumen', headers=auth_headers(token))
        assert res.status_code == 200
        data = res.get_json()
        assert 'por_nivel' in data
        assert 'total_nuevas' in data

    def test_alertas_sin_token(self, client):
        res = client.get('/api/alertas')
        assert res.status_code == 401


class TestMetricas:
    def test_metricas_sistema(self, client, token):
        if not token:
            pytest.skip("No se pudo obtener token")
        res = client.get('/api/metricas', headers=auth_headers(token))
        assert res.status_code == 200
        data = res.get_json()
        assert 'sesiones' in data
        assert 'alertas' in data
        assert 'modelo_ia' in data


class TestUsuarios:
    def test_listar_usuarios(self, client, token):
        if not token:
            pytest.skip("No se pudo obtener token")
        res = client.get('/api/usuarios', headers=auth_headers(token))
        assert res.status_code == 200
        usuarios = res.get_json()
        assert isinstance(usuarios, list)
        assert len(usuarios) > 0


class TestSesiones:
    def test_registrar_sesion(self, client, token):
        if not token:
            pytest.skip("No se pudo obtener token")
        # Obtener primer usuario
        usuarios_res = client.get('/api/usuarios', headers=auth_headers(token))
        usuarios = usuarios_res.get_json()
        usuario_id = next((u['id'] for u in usuarios if u['rol'] == 'usuario'), None)
        if not usuario_id:
            pytest.skip("No hay usuarios de tipo 'usuario'")

        res = client.post('/api/sesiones', headers=auth_headers(token), json={
            'usuario_id': usuario_id,
            'dispositivo_id': 'Test-Device',
            'ubicacion': 'Bogotá',
            'ip_acceso': '192.168.1.100',
            'tipo_acceso': 'web',
            'monto_sesion': 50000,
            'num_transacciones': 1,
        })
        assert res.status_code == 201
        data = res.get_json()
        assert 'sesion' in data
        assert 'analisis' in data
        assert 'nivel_riesgo' in data['analisis']


class TestAnalisisIA:
    def test_analizar_sesion(self, client, token):
        if not token:
            pytest.skip("No se pudo obtener token")
        usuarios_res = client.get('/api/usuarios', headers=auth_headers(token))
        usuarios = usuarios_res.get_json()
        usuario_id = next((u['id'] for u in usuarios if u['rol'] == 'usuario'), None)
        if not usuario_id:
            pytest.skip("No hay usuarios")

        res = client.post('/api/analizar', headers=auth_headers(token), json={
            'usuario_id': usuario_id,
            'dispositivo_id': 'Nuevo-Dispositivo-Sospechoso',
            'ubicacion': 'Ciudad desconocida',
            'ip_acceso': '45.33.32.156',
            'monto_sesion': 2000000,
            'num_transacciones': 15,
        })
        assert res.status_code == 200
        data = res.get_json()
        assert 'nivel_riesgo' in data
        assert data['nivel_riesgo'] in ['BAJO', 'MEDIO', 'ALTO', 'CRITICO']
