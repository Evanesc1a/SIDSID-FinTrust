"""
Script para generar datos de entrenamiento simulados para el modelo Isolation Forest.
Genera sesiones normales y anómalas balanceadas y representativas.
"""
import pandas as pd
import numpy as np
import os

np.random.seed(42)

FEATURE_COLS = [
    "hora_del_dia", "dia_semana", "dispositivo_nuevo",
    "distancia_geo_aprox", "sesiones_24h", "monto_relativo",
    "frecuencia_tx_sesion", "ip_nueva"
]


def generar_sesiones_normales(n=800):
    datos = {
        "hora_del_dia": np.random.choice(
            list(range(7, 22)), size=n,
        ),
        "dia_semana": np.random.choice(range(7), size=n,
            p=[0.16, 0.16, 0.16, 0.16, 0.16, 0.10, 0.10]),
        "dispositivo_nuevo": np.random.choice([0, 1], size=n, p=[0.95, 0.05]),
        "distancia_geo_aprox": np.random.choice([0.0, 0.5, 1.0], size=n, p=[0.85, 0.10, 0.05]),
        "sesiones_24h": np.random.poisson(2, n).clip(0, 5),
        "monto_relativo": np.random.exponential(0.8, n).clip(0, 3),
        "frecuencia_tx_sesion": np.random.poisson(2, n).clip(0, 8),
        "ip_nueva": np.random.choice([0, 1], size=n, p=[0.92, 0.08]),
        "etiqueta": 0  # normal
    }
    return pd.DataFrame(datos)


def generar_sesiones_anomalas(n=200):
    datos = {
        "hora_del_dia": np.random.choice(
            list(range(0, 6)) + list(range(23, 24)), size=n
        ),
        "dia_semana": np.random.choice(range(7), size=n),
        "dispositivo_nuevo": np.random.choice([0, 1], size=n, p=[0.20, 0.80]),
        "distancia_geo_aprox": np.random.choice([1.0, 2.0], size=n, p=[0.30, 0.70]),
        "sesiones_24h": np.random.randint(6, 20, n),
        "monto_relativo": np.random.uniform(3.0, 10.0, n),
        "frecuencia_tx_sesion": np.random.randint(10, 30, n),
        "ip_nueva": np.random.choice([0, 1], size=n, p=[0.15, 0.85]),
        "etiqueta": 1  # anomala
    }
    return pd.DataFrame(datos)


if __name__ == "__main__":
    os.makedirs("ia/data", exist_ok=True)

    normales = generar_sesiones_normales(800)
    anomalas = generar_sesiones_anomalas(200)

    normales.to_csv("ia/data/sesiones_normales.csv", index=False)
    anomalas.to_csv("ia/data/sesiones_anomalas.csv", index=False)

    print(f"Generadas {len(normales)} sesiones normales")
    print(f"Generadas {len(anomalas)} sesiones anómalas")
    print("Archivos guardados en ia/data/")
