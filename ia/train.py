"""
Entrenamiento del modelo Isolation Forest para SIDSID.
Genera y guarda el modelo entrenado como modelo.pkl
"""
import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Asegurarse de que el path es correcto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia.generate_data import generar_sesiones_normales, generar_sesiones_anomalas

FEATURE_COLS = [
    "hora_del_dia", "dia_semana", "dispositivo_nuevo",
    "distancia_geo_aprox", "sesiones_24h", "monto_relativo",
    "frecuencia_tx_sesion", "ip_nueva"
]

# Contamination: proporción esperada de anomalías
CONTAMINATION = 0.15


def entrenar_modelo():
    print("=" * 50)
    print("SIDSID — Entrenamiento del modelo Isolation Forest")
    print("=" * 50)

    # 1. Generar / cargar datos
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    data_dir = os.path.join(os.path.dirname(__file__), "data")

    norm_path = os.path.join(data_dir, "sesiones_normales.csv")
    anom_path = os.path.join(data_dir, "sesiones_anomalas.csv")

    if os.path.exists(norm_path) and os.path.exists(anom_path):
        normales = pd.read_csv(norm_path)
        anomalas = pd.read_csv(anom_path)
    else:
        normales = generar_sesiones_normales(800)
        anomalas = generar_sesiones_anomalas(200)
        normales.to_csv(norm_path, index=False)
        anomalas.to_csv(anom_path, index=False)

    print(f"Sesiones normales: {len(normales)}")
    print(f"Sesiones anómalas: {len(anomalas)}")

    # 2. Preparar datos (Isolation Forest se entrena solo con normales)
    X_train = normales[FEATURE_COLS].values
    
    # Dataset completo para evaluación
    df_eval = pd.concat([normales, anomalas], ignore_index=True)
    X_eval = df_eval[FEATURE_COLS].values
    y_eval = df_eval["etiqueta"].values  # 0=normal, 1=anomala

    # 3. Construir pipeline: scaler + Isolation Forest
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("modelo", IsolationForest(
            n_estimators=200,
            contamination=CONTAMINATION,
            max_samples="auto",
            random_state=42,
            n_jobs=-1
        ))
    ])

    # 4. Entrenar
    print("\nEntrenando modelo...")
    pipeline.fit(X_train)
    print("Modelo entrenado.")

    # 5. Evaluar
    preds_raw = pipeline.predict(X_eval)
    # Isolation Forest: -1 = anomalía, 1 = normal
    y_pred = (preds_raw == -1).astype(int)
    
    scores = pipeline.decision_function(X_eval)

    print("\n--- Métricas de Evaluación ---")
    print(classification_report(y_eval, y_pred, target_names=["Normal", "Anómala"]))
    
    tn, fp, fn, tp = confusion_matrix(y_eval, y_pred).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    print(f"Falsos Positivos: {fp}")
    print(f"Tasa de Falsos Positivos (FPR): {fpr:.3f}")

    # 6. Guardar modelo
    model_path = os.path.join(os.path.dirname(__file__), "modelo.pkl")
    joblib.dump(pipeline, model_path)
    print(f"\nModelo guardado en: {model_path}")

    # 7. Guardar métricas
    from sklearn.metrics import precision_score, recall_score, f1_score
    metricas = {
        "precision": float(precision_score(y_eval, y_pred, zero_division=0)),
        "recall": float(recall_score(y_eval, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_eval, y_pred, zero_division=0)),
        "fpr": float(fpr),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "n_train": int(len(X_train)),
        "contamination": CONTAMINATION,
    }
    metrics_path = os.path.join(os.path.dirname(__file__), "metricas.json")
    with open(metrics_path, "w") as f:
        json.dump(metricas, f, indent=2)
    print(f"Métricas guardadas en: {metrics_path}")
    return pipeline, metricas


if __name__ == "__main__":
    entrenar_modelo()
