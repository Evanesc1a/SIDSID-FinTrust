"""
Tests del módulo de IA — modelo de detección de anomalías.
Ejecutar con: python -m pytest ia/tests/test_modelo.py -v
"""
import sys
import os
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)


class TestFeatures:
    def test_extraer_features_sesion_normal(self):
        from ia.features import extraer_features

        sesion = {
            'fecha_hora': '2026-05-07T10:30:00',
            'dispositivo_id': 'iPhone-14',
            'ubicacion': 'Bogotá',
            'ip_acceso': '192.168.1.10',
            'monto_sesion': 100000,
            'num_transacciones': 2,
        }
        perfil = {
            'dispositivos_frecuentes': '["iPhone-14", "MacBook-Pro"]',
            'ubicaciones_habituales': '["Bogotá", "Medellín"]',
            'ips_habituales': '["192.168.1.10", "192.168.1.15"]',
            'monto_promedio_tx': 100000,
        }
        features = extraer_features(sesion, perfil, [])

        assert features['hora_del_dia'] == 10
        assert features['dia_semana'] == 3  # jueves (2026-05-07)
        assert features['dispositivo_nuevo'] == 0
        assert features['ip_nueva'] == 0
        assert features['monto_relativo'] == pytest.approx(1.0)

    def test_extraer_features_sesion_anomala(self):
        from ia.features import extraer_features

        sesion = {
            'fecha_hora': '2026-05-07T02:15:00',
            'dispositivo_id': 'Android-Desconocido',
            'ubicacion': 'Ciudad lejana',
            'ip_acceso': '45.33.32.156',
            'monto_sesion': 500000,
            'num_transacciones': 20,
        }
        perfil = {
            'dispositivos_frecuentes': '["iPhone-14"]',
            'ubicaciones_habituales': '["Bogotá"]',
            'ips_habituales': '["192.168.1.10"]',
            'monto_promedio_tx': 100000,
        }
        features = extraer_features(sesion, perfil, ['s1', 's2', 's3', 's4', 's5', 's6'])

        assert features['hora_del_dia'] == 2
        assert features['dispositivo_nuevo'] == 1
        assert features['ip_nueva'] == 1
        assert features['sesiones_24h'] == 6
        assert features['monto_relativo'] == pytest.approx(5.0)

    def test_features_a_array_shape(self):
        from ia.features import extraer_features, features_a_array
        sesion = {'fecha_hora': '2026-05-07T14:00:00', 'monto_sesion': 0, 'num_transacciones': 0}
        perfil = {}
        features = extraer_features(sesion, perfil, [])
        arr = features_a_array(features)
        assert arr.shape == (1, 8)

    def test_calcular_factores_riesgo(self):
        from ia.features import calcular_factores_riesgo
        features = {
            'hora_del_dia': 3,
            'dia_semana': 0,
            'dispositivo_nuevo': 1,
            'distancia_geo_aprox': 2.0,
            'sesiones_24h': 8,
            'monto_relativo': 6.0,
            'frecuencia_tx_sesion': 15,
            'ip_nueva': 1,
        }
        factores = calcular_factores_riesgo(features)
        assert len(factores) > 0
        assert any('Dispositivo' in f for f in factores)
        assert any('IP' in f for f in factores)


class TestModelo:
    def test_modelo_carga(self):
        from ia.evaluar import _cargar_modelo
        modelo = _cargar_modelo()
        assert modelo is not None

    def test_clasificar_nivel_riesgo(self):
        from ia.evaluar import clasificar_nivel_riesgo
        assert clasificar_nivel_riesgo(-0.5) == 'CRITICO'
        assert clasificar_nivel_riesgo(-0.2) == 'ALTO'
        assert clasificar_nivel_riesgo(0.01) == 'MEDIO'
        assert clasificar_nivel_riesgo(0.3) == 'BAJO'

    def test_evaluar_sesion_normal(self):
        from ia.evaluar import evaluar_sesion
        sesion = {
            'fecha_hora': '2026-05-07T10:00:00',
            'dispositivo_id': 'iPhone-14',
            'ubicacion': 'Bogotá',
            'ip_acceso': '192.168.1.1',
            'monto_sesion': 80000,
            'num_transacciones': 1,
        }
        perfil = {
            'dispositivos_frecuentes': '["iPhone-14"]',
            'ubicaciones_habituales': '["Bogotá"]',
            'ips_habituales': '["192.168.1.1"]',
            'monto_promedio_tx': 100000,
        }
        resultado = evaluar_sesion(sesion, perfil, [])
        assert 'nivel_riesgo' in resultado
        assert 'puntaje' in resultado
        assert 'es_anomala' in resultado
        assert resultado['nivel_riesgo'] in ['BAJO', 'MEDIO', 'ALTO', 'CRITICO']

    def test_evaluar_sesion_anomala(self):
        from ia.evaluar import evaluar_sesion
        sesion = {
            'fecha_hora': '2026-05-07T02:00:00',
            'dispositivo_id': 'Dispositivo-Desconocido-XYZ',
            'ubicacion': 'País extranjero',
            'ip_acceso': '45.33.32.1',
            'monto_sesion': 5000000,
            'num_transacciones': 25,
        }
        perfil = {
            'dispositivos_frecuentes': '["iPhone-14"]',
            'ubicaciones_habituales': '["Bogotá"]',
            'ips_habituales': '["192.168.1.1"]',
            'monto_promedio_tx': 100000,
        }
        sesiones_recientes = [f'sesion_{i}' for i in range(12)]
        resultado = evaluar_sesion(sesion, perfil, sesiones_recientes)
        # Una sesión tan anómala debería ser MEDIO, ALTO o CRITICO
        assert resultado['nivel_riesgo'] in ['MEDIO', 'ALTO', 'CRITICO']
