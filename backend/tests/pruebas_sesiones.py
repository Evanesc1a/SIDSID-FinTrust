"""
Script para simular sesiones de prueba y ver la detección en tiempo real.
Ejecutar con: python pruebas_sesiones.py
"""
import requests
import json

BASE = "http://localhost:5000/api"

# 1. Login para obtener token
login = requests.post(f"{BASE}/auth/login", json={
    "email": "analista@fintrust.co",
    "password": "sidsid123"
})
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Obtener un usuario de prueba
usuarios_res = requests.get(f"{BASE}/usuarios", headers=headers)
print("Status usuarios:", usuarios_res.status_code)
print("Respuesta:", usuarios_res.text[:300])
usuarios = usuarios_res.json()
usuario = next(u for u in usuarios if u["rol"] == "usuario")
uid = usuario["id"]
print(f"\nUsuario de prueba: {usuario['nombre']} ({uid[:8]}...)\n")
print("=" * 55)

# ── SESIONES DE PRUEBA ──────────────────────────────────────

sesiones = [
    {
        "nombre": "✅ Acceso NORMAL",
        "datos": {
            "usuario_id": uid,
            "dispositivo_id": "iPhone-14",       # dispositivo conocido
            "ubicacion": "Bogotá",               # ubicación habitual
            "ip_acceso": "192.168.1.10",         # IP conocida
            "tipo_acceso": "web",
            "monto_sesion": 80000,               # monto normal
            "num_transacciones": 1,
        }
    },
    {
        "nombre": "⚠️  Riesgo MEDIO — IP nueva",
        "datos": {
            "usuario_id": uid,
            "dispositivo_id": "iPhone-14",
            "ubicacion": "Bogotá",
            "ip_acceso": "45.33.32.156",         # IP sospechosa
            "tipo_acceso": "web",
            "monto_sesion": 100000,
            "num_transacciones": 2,
        }
    },
    {
        "nombre": "🔴 Riesgo ALTO — dispositivo + IP nuevos",
        "datos": {
            "usuario_id": uid,
            "dispositivo_id": "Android-Desconocido",  # dispositivo nuevo
            "ubicacion": "Medellín",
            "ip_acceso": "198.51.100.42",             # IP sospechosa
            "tipo_acceso": "web",
            "monto_sesion": 500000,                   # monto alto
            "num_transacciones": 8,
        }
    },
    {
        "nombre": "🚨 Riesgo CRÍTICO — todo anómalo",
        "datos": {
            "usuario_id": uid,
            "dispositivo_id": "Device-XYZ-Desconocido",
            "ubicacion": "País extranjero",
            "ip_acceso": "91.195.240.117",
            "tipo_acceso": "web",
            "monto_sesion": 4500000,             # 45x el promedio
            "num_transacciones": 20,             # muchas transacciones
        }
    },
]

for s in sesiones:
    res = requests.post(f"{BASE}/sesiones", headers=headers, json=s["datos"])
    data = res.json()
    analisis = data.get("analisis", {})
    alerta = data.get("alerta_creada")

    print(f"\n{s['nombre']}")
    print(f"  Nivel de riesgo : {analisis.get('nivel_riesgo')}")
    print(f"  Puntaje anomalía: {analisis.get('puntaje', 0):.4f}")
    print(f"  Es anómala      : {analisis.get('es_anomala')}")
    if analisis.get("factores"):
        print(f"  Factores        : {', '.join(analisis['factores'][:2])}")
    if alerta:
        print(f"  ⚡ Alerta creada : {alerta['id'][:8]}... [{alerta['nivel_riesgo']}]")

print("\n" + "=" * 55)
print("Revisa las alertas en: http://localhost:3000/alertas")