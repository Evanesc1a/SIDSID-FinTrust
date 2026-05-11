"""
seed_data.py — FinTrust SIDSID
================================
Genera datos sintéticos realistas para poblar la base de datos
de entrenamiento del modelo Isolation Forest.

Requisitos:
    pip install faker pymysql bcrypt

Uso:
    # Ajusta DB_CONFIG al inicio del archivo y luego:
    python seed_data.py

Qué genera:
    - 3 analistas de seguridad
    - 50 usuarios finales con perfil de comportamiento
    - ~800 sesiones normales (patrones consistentes por usuario)
    - ~40 sesiones anómalas (patrones deliberadamente rotos)
    - Transacciones por cada sesión
    - Intentos de autenticación (exitosos y fallidos)
    - Features calculados en datos_entrenamiento_ia
    - Alertas para las sesiones de riesgo ALTO / CRITICO
    - 1 registro de métricas del modelo (baseline)
"""

import json
import random
import math
from datetime import datetime, timedelta

import bcrypt
import pymysql
from faker import Faker
from faker.providers import internet, person, address, phone_number

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "root123",          # ← cambia por la contraseña
    "database": "fintrust",
    "charset":  "utf8mb4",
}

SEED = 42                         # reproducibilidad
NUM_USUARIOS          = 50
NUM_SESIONES_NORMALES = 800       # distribuidas entre los 50 usuarios
NUM_SESIONES_ANOMALAS = 40        # sesiones con patrones rotos
# ──────────────────────────────────────────────────────────────────────────────

fake = Faker("es_CO")
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(address)
fake.add_provider(phone_number)
random.seed(SEED)
Faker.seed(SEED)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def hash_pwd(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def rand_ip_colombia() -> str:
    """IP colombiana ficticia dentro de rangos comunes."""
    prefixes = ["181.132", "190.25", "186.29", "200.21", "181.53", "190.147"]
    prefix = random.choice(prefixes)
    return f"{prefix}.{random.randint(1,254)}.{random.randint(1,254)}"


def rand_ip_foreign() -> str:
    """IP de otro país (para sesión anómala)."""
    prefixes = ["193.26", "104.248", "45.33", "178.62", "54.36"]
    prefix = random.choice(prefixes)
    return f"{prefix}.{random.randint(1,254)}.{random.randint(1,254)}"


def rand_device_normal() -> str:
    devices = [
        "Android-Chrome/120", "iOS-Safari/17", "Windows-Chrome/121",
        "Windows-Firefox/122", "macOS-Safari/17", "Android-Samsung/14",
    ]
    return random.choice(devices)


def rand_device_anomalous() -> str:
    devices = [
        "Linux-curl/7.88", "Windows-Edge/91", "Unknown-Bot/1.0",
        "Postman/10.0", "Python-requests/2.31",
    ]
    return random.choice(devices)


def rand_hora_normal() -> int:
    """Hora de acceso habitual: entre 7am y 10pm (sesgo gaussiano)."""
    h = int(random.gauss(14, 3))    # media: 2pm
    return max(7, min(22, h))


def rand_hora_anomalous() -> int:
    """Hora de acceso anómala: madrugada."""
    return random.randint(0, 5)


def normalizar_hora(hora: int, minuto: int = 0) -> float:
    return round((hora * 60 + minuto) / 1439, 4)


def haversine(lat1, lon1, lat2, lon2) -> float:
    """Distancia en km entre dos puntos geográficos."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi   = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(2 * R * math.asin(math.sqrt(a)), 2)


# Coordenadas aproximadas de ciudades colombianas principales
CIUDADES_CO = {
    "Bucaramanga":  (7.1193,  -73.1227),
    "Bogotá":       (4.7110,  -74.0721),
    "Medellín":     (6.2442,  -75.5812),
    "Cali":         (3.4516,  -76.5319),
    "Barranquilla": (10.9685, -74.7813),
    "Cartagena":    (10.3910, -75.4794),
    "Cúcuta":       (7.8939,  -72.5078),
    "Pereira":      (4.8133,  -75.6961),
}

CIUDADES_EXTRANJERAS = {
    "Miami":    (25.7617, -80.1918),
    "Madrid":   (40.4168,  -3.7038),
    "Bogotá":   (4.7110,  -74.0721),   # "mismo nombre, diferente IP"
    "São Paulo":(-23.5505, -46.6333),
}


# ─── CONEXIÓN ─────────────────────────────────────────────────────────────────

def get_connection():
    return pymysql.connect(**DB_CONFIG, autocommit=False)


# ─── INSERCIÓN ANALISTAS ──────────────────────────────────────────────────────

def seed_analistas(cur) -> list[int]:
    analistas = [
        ("Carlos Ramírez",    "c.ramirez@fintrust.com.co",  "analista"),
        ("Diana Morales",     "d.morales@fintrust.com.co",  "analista"),
        ("Andrés Quintero",   "a.quintero@fintrust.com.co", "supervisor"),
    ]
    ids = []
    for nombre, email, rol in analistas:
        cur.execute(
            """INSERT INTO analistas (nombre, email, hash_password, rol)
               VALUES (%s, %s, %s, %s)""",
            (nombre, email, hash_pwd("Fintrust2025!"), rol),
        )
        ids.append(cur.lastrowid)
    print(f"  ✓ {len(ids)} analistas insertados")
    return ids


# ─── INSERCIÓN USUARIOS + PERFILES ────────────────────────────────────────────

def seed_usuarios(cur) -> list[dict]:
    """Crea NUM_USUARIOS usuarios con sus perfiles de comportamiento."""
    users = []
    segmentos = ["no_bancarizado", "no_bancarizado", "bancarizado", "pyme"]

    for _ in range(NUM_USUARIOS):
        nombre   = fake.name()
        email    = fake.unique.email()
        telefono = fake.phone_number()
        seg      = random.choice(segmentos)
        ciudad   = random.choice(list(CIUDADES_CO.keys()))
        lat, lon = CIUDADES_CO[ciudad]

        # Dispositivos y IPs habituales (1-3 por usuario)
        dispositivos = random.sample([
            "Android-Chrome/120", "iOS-Safari/17", "Windows-Chrome/121",
            "Windows-Firefox/122", "macOS-Safari/17",
        ], k=random.randint(1, 3))

        ips = [rand_ip_colombia() for _ in range(random.randint(1, 2))]

        hora_inicio  = random.randint(7, 10)
        hora_fin     = random.randint(20, 23)
        horario      = f"{hora_inicio:02d}:00-{hora_fin:02d}:00"

        # Monto promedio según segmento (en COP)
        if seg == "pyme":
            umbral = round(random.uniform(500_000, 5_000_000), 2)
        elif seg == "bancarizado":
            umbral = round(random.uniform(100_000, 1_000_000), 2)
        else:
            umbral = round(random.uniform(10_000, 200_000), 2)

        cur.execute(
            """INSERT INTO usuarios
               (email, nombre, hash_password, telefono, segmento)
               VALUES (%s, %s, %s, %s, %s)""",
            (email, nombre, hash_pwd("Pass1234!"), telefono, seg),
        )
        uid = cur.lastrowid

        cur.execute(
            """INSERT INTO perfiles_comportamiento
               (usuario_id, dispositivos_habituales, ips_habituales,
                horario_tipico, umbral_monto, ubicacion_habitual,
                frecuencia_semanal_avg)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                uid,
                json.dumps(dispositivos),
                json.dumps(ips),
                horario,
                umbral,
                ciudad,
                round(random.uniform(2, 15), 1),
            ),
        )

        users.append({
            "id":           uid,
            "dispositivos": dispositivos,
            "ips":          ips,
            "hora_inicio":  hora_inicio,
            "hora_fin":     hora_fin,
            "umbral":       umbral,
            "ciudad":       ciudad,
            "lat":          lat,
            "lon":          lon,
            "segmento":     seg,
        })

    print(f"  ✓ {len(users)} usuarios + perfiles insertados")
    return users


# ─── SESIÓN + TRANSACCIONES + ENTRENAMIENTO ───────────────────────────────────

def _insert_sesion_y_features(
    cur,
    usuario: dict,
    fecha_base: datetime,
    es_anomala: bool,
    anomalia_tipo: str | None = None,
) -> int:
    """
    Inserta una sesión, sus transacciones y el vector de features
    en datos_entrenamiento_ia. Devuelve el sesion_id.
    """
    u = usuario

    # ── Parámetros según tipo ────────────────────────────────────────────────
    if not es_anomala:
        hora   = random.randint(u["hora_inicio"], u["hora_fin"])
        minuto = random.randint(0, 59)
        ip     = random.choice(u["ips"])
        device = random.choice(u["dispositivos"])
        ciudad = u["ciudad"]
        lat    = u["lat"] + random.uniform(-0.05, 0.05)
        lon    = u["lon"] + random.uniform(-0.05, 0.05)
        monto_factor  = random.uniform(0.5, 1.5)
        fallos_24h    = random.choices([0, 1], weights=[90, 10])[0]
        nivel_riesgo  = "BAJO"
        puntaje       = round(random.uniform(0.05, 0.25), 4)

    else:
        # Tipos de anomalía posibles
        tipo = anomalia_tipo or random.choice([
            "hora_extraña",
            "ip_desconocida",
            "dispositivo_raro",
            "ubicacion_lejana",
            "monto_excesivo",
            "multiples_fallos",
            "combinado",          # varios factores a la vez
        ])

        # Valores base (luego se pisan según el tipo)
        hora   = random.randint(u["hora_inicio"], u["hora_fin"])
        minuto = random.randint(0, 59)
        ip     = random.choice(u["ips"])
        device = random.choice(u["dispositivos"])
        ciudad = u["ciudad"]
        lat    = u["lat"]
        lon    = u["lon"]
        monto_factor = random.uniform(0.5, 1.5)
        fallos_24h   = 0

        if tipo in ("hora_extraña", "combinado"):
            hora   = rand_hora_anomalous()
            minuto = random.randint(0, 59)

        if tipo in ("ip_desconocida", "combinado"):
            ip = rand_ip_foreign()

        if tipo in ("dispositivo_raro", "combinado"):
            device = rand_device_anomalous()

        if tipo in ("ubicacion_lejana", "combinado"):
            ciudad_ext, (lat_ext, lon_ext) = random.choice(
                list(CIUDADES_EXTRANJERAS.items())
            )
            ciudad = ciudad_ext
            lat    = lat_ext + random.uniform(-0.1, 0.1)
            lon    = lon_ext + random.uniform(-0.1, 0.1)

        if tipo in ("monto_excesivo", "combinado"):
            monto_factor = random.uniform(8, 25)   # 8-25× el promedio habitual

        if tipo in ("multiples_fallos", "combinado"):
            fallos_24h = random.randint(4, 10)

        # Niveles de riesgo asignados según cantidad de factores anómalos
        factores = sum([
            hora < 6 or hora > 23,
            ip not in u["ips"],
            device not in u["dispositivos"],
            haversine(u["lat"], u["lon"], lat, lon) > 100,
            monto_factor > 5,
            fallos_24h >= 3,
        ])
        if   factores >= 4: nivel_riesgo = "CRITICO"; puntaje = round(random.uniform(-0.9, -0.7), 4)
        elif factores >= 3: nivel_riesgo = "ALTO";    puntaje = round(random.uniform(-0.7, -0.5), 4)
        elif factores >= 2: nivel_riesgo = "MEDIO";   puntaje = round(random.uniform(-0.5, -0.3), 4)
        else:               nivel_riesgo = "BAJO";    puntaje = round(random.uniform(-0.3, -0.1), 4)

    # ── Fechas de sesión ─────────────────────────────────────────────────────
    hora_inicio = fecha_base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    duracion    = timedelta(minutes=random.randint(2, 45))
    hora_fin    = hora_inicio + duracion

    # ── INSERT sesion ────────────────────────────────────────────────────────
    distancia = haversine(u["lat"], u["lon"], lat, lon)

    cur.execute(
        """INSERT INTO sesiones
           (usuario_id, ip, dispositivo, ubicacion, latitud, longitud,
            hora_inicio, hora_fin, puntaje_anomalia, nivel_riesgo, es_anomala)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            u["id"], ip, device, ciudad,
            round(lat, 6), round(lon, 6),
            hora_inicio, hora_fin,
            puntaje, nivel_riesgo,
            1 if es_anomala else 0,
        ),
    )
    sesion_id = cur.lastrowid

    # ── INSERT transacciones ─────────────────────────────────────────────────
    tipos_txn    = ["pago", "transferencia", "recarga", "retiro", "credito"]
    num_txn      = random.randint(1, 6)
    monto_max    = 0.0
    for _ in range(num_txn):
        monto = round(u["umbral"] * monto_factor * random.uniform(0.3, 1.2), 2)
        monto = max(1_000, monto)
        monto_max = max(monto_max, monto)
        estado = random.choices(
            ["completada", "pendiente", "fallida"],
            weights=[80, 15, 5],
        )[0]
        cur.execute(
            """INSERT INTO transacciones
               (sesion_id, tipo, monto, estado, es_sospechosa, hora)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                sesion_id,
                random.choice(tipos_txn),
                monto,
                estado,
                1 if es_anomala and monto_factor > 5 else 0,
                hora_inicio + timedelta(minutes=random.randint(1, int(duracion.seconds/60) or 1)),
            ),
        )

    # ── INSERT features de entrenamiento ────────────────────────────────────
    dispositivo_conocido = 1 if device in u["dispositivos"] else 0
    ip_conocida          = 1 if ip in u["ips"] else 0

    cur.execute(
        """INSERT INTO datos_entrenamiento_ia
           (sesion_id, hora_normalizada, dia_semana,
            frecuencia_acceso_7d, intentos_fallidos_24h,
            dispositivo_conocido, ip_conocida, distancia_geo_km,
            monto_promedio_historico, num_transacciones_sesion,
            monto_maximo_sesion, puntaje_asignado, etiqueta_fraude)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            sesion_id,
            normalizar_hora(hora, minuto),
            fecha_base.weekday(),
            random.randint(2, 20),
            fallos_24h,
            dispositivo_conocido,
            ip_conocida,
            distancia,
            u["umbral"],
            num_txn,
            round(monto_max, 2),
            puntaje,
            1 if es_anomala else 0,
        ),
    )

    return sesion_id


# ─── INTENTOS DE AUTENTICACIÓN ────────────────────────────────────────────────

def seed_intentos(cur, users: list[dict]) -> None:
    """Genera intentos de login fallidos distribuidos entre los usuarios."""
    motivos = [
        "contraseña_incorrecta",
        "usuario_no_encontrado",
        "sesion_expirada",
        "token_invalido",
    ]
    count = 0
    for u in users:
        # Entre 0 y 5 intentos fallidos por usuario en el pasado mes
        n_fallos = random.choices([0, 1, 2, 3, 4, 5], weights=[40,25,15,10,6,4])[0]
        for _ in range(n_fallos):
            fecha = fake.date_time_between(start_date="-30d", end_date="now")
            cur.execute(
                """INSERT INTO intentos_autenticacion
                   (usuario_id, ip, dispositivo, exitoso, motivo_fallo, fecha)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    u["id"],
                    rand_ip_colombia(),
                    rand_device_normal(),
                    0,
                    random.choice(motivos),
                    fecha,
                ),
            )
            count += 1
        # Un intento exitoso reciente (el último login normal)
        cur.execute(
            """INSERT INTO intentos_autenticacion
               (usuario_id, ip, dispositivo, exitoso, fecha)
               VALUES (%s,%s,%s,%s,%s)""",
            (
                u["id"],
                random.choice(u["ips"]),
                random.choice(u["dispositivos"]),
                1,
                fake.date_time_between(start_date="-7d", end_date="now"),
            ),
        )
    print(f"  ✓ Intentos de autenticación insertados ({count} fallidos)")


# ─── ALERTAS ─────────────────────────────────────────────────────────────────

def seed_alertas(cur, sesiones_anomalas: list[tuple], analistas: list[int]) -> None:
    """
    Crea alertas para las sesiones de riesgo MEDIO, ALTO y CRITICO.
    sesiones_anomalas: lista de (sesion_id, nivel_riesgo)
    """
    descripciones = {
        "MEDIO":   "Acceso desde dispositivo o IP no habitual. Requiere monitoreo.",
        "ALTO":    "Múltiples factores anómalos detectados. Se recomienda autenticación reforzada.",
        "CRITICO": "Patrón de acceso completamente fuera del perfil. Posible suplantación activa.",
    }
    acciones = {
        "MEDIO":   "autenticacion_reforzada",
        "ALTO":    "bloqueo_preventivo",
        "CRITICO": "bloqueo_definitivo",
    }
    count = 0
    for sesion_id, nivel in sesiones_anomalas:
        if nivel == "BAJO":
            continue  # Las sesiones de riesgo BAJO no generan alerta

        # 70% ya resueltas (para tener datos históricos de entrenamiento)
        resuelta = random.random() < 0.70
        analista_id = random.choice(analistas)

        decision     = "PENDIENTE"
        motivo_desc  = None
        fecha_res    = None
        accion       = "ninguna"

        if resuelta:
            # 65% confirmadas como fraude, 35% falso positivo
            if random.random() < 0.65:
                decision = "CONFIRMADO_FRAUDE"
                accion   = acciones[nivel]
            else:
                decision    = "FALSO_POSITIVO"
                motivo_desc = random.choice([
                    "Usuario viajando al exterior — confirmado por llamada.",
                    "Dispositivo nuevo registrado por el propio usuario.",
                    "Transacción confirmada como legítima por el titular.",
                    "IP corporativa no registrada en el perfil.",
                ])
                accion = "ninguna"
            fecha_res = fake.date_time_between(start_date="-14d", end_date="now")

        cur.execute(
            """INSERT INTO alertas
               (sesion_id, analista_id, nivel_riesgo, descripcion,
                resuelta, decision_analista, motivo_descarte,
                accion_tomada, fecha_resolucion)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                sesion_id,
                analista_id,
                nivel,
                descripciones[nivel],
                1 if resuelta else 0,
                decision,
                motivo_desc,
                accion,
                fecha_res,
            ),
        )
        count += 1

    print(f"  ✓ {count} alertas insertadas")


# ─── MÉTRICAS BASELINE ────────────────────────────────────────────────────────

def seed_metricas(cur) -> None:
    cur.execute(
        """INSERT INTO metricas_modelo
           (version_modelo, contaminacion, n_estimadores,
            precision_score, recall_score, f1_score,
            tasa_falsos_positivos, tasa_deteccion_temprana,
            total_sesiones, total_alertas,
            alertas_confirmadas, alertas_descartadas,
            tiempo_respuesta_avg_min, notas)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            "v0.1.0-baseline",
            0.05,                  # 5% contaminación estimada (proporción de fraudes)
            100,                   # n_estimators
            0.78,                  # precision
            0.72,                  # recall
            0.75,                  # F1
            0.22,                  # tasa falsos positivos
            0.68,                  # tasa detección temprana
            NUM_SESIONES_NORMALES + NUM_SESIONES_ANOMALAS,
            NUM_SESIONES_ANOMALAS,
            int(NUM_SESIONES_ANOMALAS * 0.65),
            int(NUM_SESIONES_ANOMALAS * 0.35),
            14.5,
            "Modelo baseline entrenado con datos sintéticos. "
            "Pendiente reentrenamiento con datos reales.",
        ),
    )
    print("  ✓ Métricas baseline insertadas")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n🚀 Iniciando seed de FinTrust SIDSID...")
    conn = get_connection()
    cur  = conn.cursor()

    try:
        print("\n[1/7] Insertando analistas...")
        analistas = seed_analistas(cur)

        print("[2/7] Insertando usuarios y perfiles de comportamiento...")
        users = seed_usuarios(cur)

        print("[3/7] Insertando sesiones normales (~800)...")
        fecha_inicio = datetime.now() - timedelta(days=90)
        sesion_count = 0
        for _ in range(NUM_SESIONES_NORMALES):
            usuario    = random.choice(users)
            fecha_base = fake.date_time_between(
                start_date=fecha_inicio,
                end_date=datetime.now(),
            )
            _insert_sesion_y_features(cur, usuario, fecha_base, es_anomala=False)
            sesion_count += 1
        print(f"  ✓ {sesion_count} sesiones normales insertadas")

        print("[4/7] Insertando sesiones anómalas (~40)...")
        sesiones_anomalas = []
        tipos_anomalia = [
            "hora_extraña", "ip_desconocida", "dispositivo_raro",
            "ubicacion_lejana", "monto_excesivo", "multiples_fallos", "combinado",
        ]
        for i in range(NUM_SESIONES_ANOMALAS):
            usuario    = random.choice(users)
            fecha_base = fake.date_time_between(
                start_date=fecha_inicio,
                end_date=datetime.now(),
            )
            tipo = tipos_anomalia[i % len(tipos_anomalia)]
            sid  = _insert_sesion_y_features(
                cur, usuario, fecha_base, es_anomala=True, anomalia_tipo=tipo
            )
            # Recuperar el nivel_riesgo recién insertado
            cur.execute("SELECT nivel_riesgo FROM sesiones WHERE id = %s", (sid,))
            nivel = cur.fetchone()[0]
            sesiones_anomalas.append((sid, nivel))
        print(f"  ✓ {NUM_SESIONES_ANOMALAS} sesiones anómalas insertadas")

        print("[5/7] Insertando intentos de autenticación...")
        seed_intentos(cur, users)

        print("[6/7] Insertando alertas...")
        seed_alertas(cur, sesiones_anomalas, analistas)

        print("[7/7] Insertando métricas del modelo baseline...")
        seed_metricas(cur)

        conn.commit()
        print("\n✅ Seed completado exitosamente.")
        print(f"   → Usuarios:             {NUM_USUARIOS}")
        print(f"   → Sesiones normales:    {NUM_SESIONES_NORMALES}")
        print(f"   → Sesiones anómalas:    {NUM_SESIONES_ANOMALAS}")
        print(f"   → Total en entrenamiento: {NUM_SESIONES_NORMALES + NUM_SESIONES_ANOMALAS}")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error durante el seed: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
