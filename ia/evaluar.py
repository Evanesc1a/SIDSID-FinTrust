"""
Módulo de evaluación del modelo Isolation Forest.
Expone la función principal para analizar una sesión.
"""
import os
import json
import joblib
import numpy as np

from ia.features import extraer_features, features_a_array, calcular_factores_riesgo

_modelo = None
MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo.pkl")

UMBRALES = {
    # score de anomalía normalizado (más negativo = más anómalo)
    "CRITICO": -0.3,
    "ALTO":    -0.1,
    "MEDIO":    0.05,
    # por encima = BAJO
}


def _cargar_modelo():
    global _modelo
    if _modelo is None:
        if not os.path.exists(MODEL_PATH):
            # Entrenar automáticamente si no existe
            from ia.train import entrenar_modelo
            entrenar_modelo()
        _modelo = joblib.load(MODEL_PATH)
    return _modelo


def clasificar_nivel_riesgo(score: float) -> str:
    """Clasifica el nivel de riesgo basado en el score de anomalía."""
    if score <= UMBRALES["CRITICO"]:
        return "CRITICO"
    elif score <= UMBRALES["ALTO"]:
        return "ALTO"
    elif score <= UMBRALES["MEDIO"]:
        return "MEDIO"
    else:
        return "BAJO"


def evaluar_sesion(sesion_data: dict, perfil: dict, sesiones_recientes: list) -> dict:
    """
    Evalúa una sesión y retorna el resultado del análisis de anomalías.
    
    Returns:
        {
            "puntaje": float,          # score de anomalía (-1 a 1, más negativo = más anómalo)
            "es_anomala": bool,
            "nivel_riesgo": str,       # BAJO / MEDIO / ALTO / CRITICO
            "factores": list[str],     # factores que contribuyeron
            "features": dict,          # valores de features para trazabilidad
        }
    """
    modelo = _cargar_modelo()
    
    features = extraer_features(sesion_data, perfil, sesiones_recientes)
    X = features_a_array(features)
    
    # decision_function: cuanto más negativo, más anómalo
    score = float(modelo.decision_function(X)[0])
    prediccion = modelo.predict(X)[0]  # -1 = anomalía, 1 = normal
    
    es_anomala = prediccion == -1
    nivel_riesgo = clasificar_nivel_riesgo(score)
    
    factores = []
    if es_anomala or nivel_riesgo in ("MEDIO", "ALTO", "CRITICO"):
        factores = calcular_factores_riesgo(features)

    return {
        "puntaje": float(score),
        "es_anomala": bool(es_anomala),
        "nivel_riesgo": nivel_riesgo,
        "factores": factores,
        "features": {k: float(v) for k, v in features.items()},
    }
