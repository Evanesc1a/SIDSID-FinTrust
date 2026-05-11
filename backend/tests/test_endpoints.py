"""
Tests de integración para los endpoints principales de SIDSID.
Ejecutar: pytest tests/ -v
"""
import pytest


# ══════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════

class TestAuth:
    def test_login_analista_ok(self, client):
        r = client.post("/auth/login/analista",
                        json={"email": "test.analista@fintrust.com", "password": "Test1234!"})
        assert r.status_code == 200
        data = r.get_json()
        assert "access_token" in data
        assert data["tipo"] == "analista"

    def test_login_analista_credenciales_invalidas(self, client):
        r = client.post("/auth/login/analista",
                        json={"email": "test.analista@fintrust.com", "password": "WRONG"})
        assert r.status_code == 401

    def test_login_usuario_ok(self, client):
        r = client.post("/auth/login/usuario",
                        json={"email": "test.usuario@example.com", "password": "Test1234!"})
        assert r.status_code == 200
        data = r.get_json()
        assert "access_token" in data
        assert data["tipo"] == "usuario"

    def test_login_usuario_campos_vacios(self, client):
        r = client.post("/auth/login/usuario", json={})
        assert r.status_code == 400

    def test_me_sin_token(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 401

    def test_me_con_token(self, client, token_analista):
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token_analista}"})
        assert r.status_code == 200
        assert r.get_json()["tipo"] == "analista"


# ══════════════════════════════════════════════════════════
#  SESIONES
# ══════════════════════════════════════════════════════════

class TestSesiones:
    def test_crear_sesion_ok(self, client, token_usuario):
        r = client.post("/sesiones",
                        json={"ip": "190.25.1.1", "dispositivo": "Android-Chrome/120",
                              "ubicacion": "Bogotá"},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        assert r.status_code == 201
        data = r.get_json()
        assert data["id"] is not None
        assert data["nivel_riesgo"] == "BAJO"
        return data["id"]

    def test_crear_sesion_sin_token(self, client):
        r = client.post("/sesiones", json={"ip": "1.2.3.4"})
        assert r.status_code == 401

    def test_obtener_sesion(self, client, token_usuario):
        # Crear primero
        r = client.post("/sesiones",
                        json={"ip": "190.25.1.1"},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        sid = r.get_json()["id"]
        # Obtener
        r2 = client.get(f"/sesiones/{sid}",
                        headers={"Authorization": f"Bearer {token_usuario}"})
        assert r2.status_code == 200
        assert r2.get_json()["id"] == sid

    def test_sesion_no_existente(self, client, token_usuario):
        r = client.get("/sesiones/99999",
                       headers={"Authorization": f"Bearer {token_usuario}"})
        assert r.status_code == 404

    def test_crear_transaccion(self, client, token_usuario):
        r = client.post("/sesiones",
                        json={"ip": "190.25.1.1"},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        sid = r.get_json()["id"]
        r2 = client.post(f"/sesiones/{sid}/transacciones",
                         json={"tipo": "pago", "monto": 50000},
                         headers={"Authorization": f"Bearer {token_usuario}"})
        assert r2.status_code == 201
        assert r2.get_json()["tipo"] == "pago"

    def test_transaccion_tipo_invalido(self, client, token_usuario):
        r = client.post("/sesiones",
                        json={"ip": "190.25.1.1"},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        sid = r.get_json()["id"]
        r2 = client.post(f"/sesiones/{sid}/transacciones",
                         json={"tipo": "TIPO_INVALIDO", "monto": 100},
                         headers={"Authorization": f"Bearer {token_usuario}"})
        assert r2.status_code == 422


# ══════════════════════════════════════════════════════════
#  ANÁLISIS IA
# ══════════════════════════════════════════════════════════

class TestAnalisis:
    def _crear_sesion(self, client, token_usuario, ip="190.25.1.1"):
        r = client.post("/sesiones", json={"ip": ip, "dispositivo": "Android-Chrome/120"},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        return r.get_json()["id"]

    def test_analizar_sesion_normal(self, client, token_usuario):
        sid = self._crear_sesion(client, token_usuario)
        r = client.post("/api/analizar",
                        json={"sesion_id": sid},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        assert r.status_code == 200
        data = r.get_json()
        assert "nivel" in data
        assert data["nivel"] in ("BAJO", "MEDIO", "ALTO", "CRITICO")

    def test_analizar_sesion_anomala(self, client, token_usuario):
        """IP extranjera + dispositivo sospechoso debe generar nivel alto."""
        sid = self._crear_sesion(client, token_usuario, ip="193.26.1.100")
        # Agregar dispositivo sospechoso actualizando la sesión vía BD directamente
        from config.database import db
        from models.sesion import Sesion
        with client.application.app_context():
            s = db.session.get(Sesion, sid)
            s.dispositivo = "Python-requests/2.31"
            db.session.commit()

        r = client.post("/api/analizar",
                        json={"sesion_id": sid},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        assert r.status_code == 200
        data = r.get_json()
        assert data["nivel"] in ("MEDIO", "ALTO", "CRITICO")

    def test_analizar_sin_sesion_id(self, client, token_usuario):
        r = client.post("/api/analizar", json={},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        assert r.status_code == 400

    def test_analizar_doble_falla(self, client, token_usuario):
        """Analizar la misma sesión dos veces debe retornar 200 (idempotente)."""
        sid = self._crear_sesion(client, token_usuario)
        client.post("/api/analizar", json={"sesion_id": sid},
                    headers={"Authorization": f"Bearer {token_usuario}"})
        r = client.post("/api/analizar", json={"sesion_id": sid},
                        headers={"Authorization": f"Bearer {token_usuario}"})
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════
#  ALERTAS
# ══════════════════════════════════════════════════════════

class TestAlertas:
    def test_listar_alertas(self, client, token_analista):
        r = client.get("/alertas",
                       headers={"Authorization": f"Bearer {token_analista}"})
        assert r.status_code == 200
        data = r.get_json()
        assert "alertas" in data
        assert "total" in data

    def test_listar_alertas_filtro_nivel(self, client, token_analista):
        r = client.get("/alertas?nivel=CRITICO",
                       headers={"Authorization": f"Bearer {token_analista}"})
        assert r.status_code == 200

    def test_alerta_no_existente(self, client, token_analista):
        r = client.get("/alertas/99999",
                       headers={"Authorization": f"Bearer {token_analista}"})
        assert r.status_code == 404


# ══════════════════════════════════════════════════════════
#  MÉTRICAS
# ══════════════════════════════════════════════════════════

class TestMetricas:
    def test_dashboard_kpis(self, client, token_analista):
        r = client.get("/metricas",
                       headers={"Authorization": f"Bearer {token_analista}"})
        assert r.status_code == 200
        data = r.get_json()
        assert "alertas" in data
        assert "sesiones" in data
        assert "usuarios" in data
        assert "modelo" in data

    def test_reporte_incidentes(self, client, token_analista):
        r = client.get("/metricas/reporte-incidentes",
                       headers={"Authorization": f"Bearer {token_analista}"})
        assert r.status_code == 200
        data = r.get_json()
        assert "registros" in data


# ══════════════════════════════════════════════════════════
#  USUARIOS (solo analistas)
# ══════════════════════════════════════════════════════════

class TestUsuarios:
    def test_listar_usuarios_como_analista(self, client, token_analista):
        r = client.get("/usuarios",
                       headers={"Authorization": f"Bearer {token_analista}"})
        assert r.status_code == 200

    def test_listar_usuarios_como_usuario_falla(self, client, token_usuario):
        r = client.get("/usuarios",
                       headers={"Authorization": f"Bearer {token_usuario}"})
        assert r.status_code == 403

    def test_health_check(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.get_json()["status"] == "ok"
