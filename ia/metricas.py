"""
Módulo para obtener métricas del modelo de IA.
"""
import os
import json


def obtener_metricas_modelo() -> dict:
    """Retorna las métricas del último entrenamiento del modelo."""
    metrics_path = os.path.join(os.path.dirname(__file__), "metricas.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    return {
        "precision": 0.0,
        "recall": 0.0,
        "f1_score": 0.0,
        "fpr": 0.0,
        "mensaje": "Modelo no entrenado aún"
    }
