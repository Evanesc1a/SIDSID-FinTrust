"""
Script de seed: pobla la base de datos con datos simulados realistas.
Crea analistas, usuarios finales, sesiones, transacciones y alertas.
"""
import sys
import os
import uuid
import json
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Asegurar que el path raíz esté disponible
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from backend.config.database import SessionLocal, init_db
from backend.models.usuario import Usuario
from backend.models.sesion import Sesion
from backend.models.perfil import PerfilComportamiento
from backend.models.transaccion import Transaccion
from backend.models.alerta import Alerta

DISPOSITIVOS = ["iPhone-14", "Samsung-S23", "MacBook-Pro", "Windows-PC", "iPad-Air", "Pixel-7"]
UBICACIONES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga"]
IPS_NORMALES = [f"192.168.{random.randint(1,10)}.{random.randint(1,254)}" for _ in range(20)]
IPS_SOSPECHOSAS = ["45.33.32.156", "198.51.100.42", "203.0.113.7", "91.195.240.117"]

NOMBRES = [
    "Ana García", "Carlos López", "María Rodríguez", "Juan Martínez",
    "Laura Hernández", "Pedro Gómez", "Sofía Díaz", "Andrés Torres",
    "Isabella Vargas", "Diego Morales", "Valentina Ruiz", "Santiago Jiménez",
    "Camila Flores", "Sebastián Castillo", "Natalia Romero", "Mateo Herrera"
]


def crear_usuarios_analistas(db):
    analistas = [
        {"nombre": "Admin SIDSID", "email": "admin@fintrust.co", "rol": "admin"},
        {"nombre": "Ana Seguridad", "email": "analista@fintrust.co", "rol": "analista"},
        {"nombre": "Carlos Monitor", "email": "monitor@fintrust.co", "rol": "analista"},
    ]
    creados = []
    for a in analistas:
        if not db.query(Usuario).filter_by(email=a["email"]).first():
            u = Usuario(
                id=str(uuid.uuid4()),
                nombre=a["nombre"],
                email=a["email"],
                password_hash=generate_password_hash("sidsid123"),
                rol=a["rol"],
                estado="ACTIVA",
            )
            db.add(u)
            creados.append(u)
    db.commit()
    print(f"  Analistas creados: {len(creados)}")
    return creados


def crear_usuarios_finales(db, n=16):
    creados = []
    for i, nombre in enumerate(NOMBRES[:n]):
        email = f"usuario{i+1}@fintrust.co"
        if not db.query(Usuario).filter_by(email=email).first():
            u = Usuario(
                id=str(uuid.uuid4()),
                nombre=nombre,
                email=email,
                password_hash=generate_password_hash("user123"),
                rol="usuario",
                estado="ACTIVA" if i < 14 else "BLOQUEADA",
            )
            db.add(u)
            creados.append(u)
    db.commit()
    print(f"  Usuarios finales creados: {len(creados)}")
    return creados


def crear_perfiles(db, usuarios):
    for u in usuarios:
        if not db.query(PerfilComportamiento).filter_by(usuario_id=u.id).first():
            dispositivos = random.sample(DISPOSITIVOS, k=random.randint(1, 3))
            ubicaciones = random.sample(UBICACIONES[:3], k=random.randint(1, 2))
            horarios = random.sample(range(7, 22), k=random.randint(3, 6))
            ips = random.sample(IPS_NORMALES, k=random.randint(2, 5))

            perfil = PerfilComportamiento(
                usuario_id=u.id,
                dispositivos_frecuentes=json.dumps(dispositivos),
                horarios_habituales=json.dumps(horarios),
                ubicaciones_habituales=json.dumps(ubicaciones),
                ips_habituales=json.dumps(ips),
                frecuencia_tx=random.uniform(1.0, 5.0),
                monto_promedio_tx=random.uniform(50000, 500000),
                sesiones_promedio_dia=random.uniform(0.5, 3.0),
                ultima_actualizacion=datetime.utcnow(),
            )
            db.add(perfil)
    db.commit()
    print(f"  Perfiles creados: {len(usuarios)}")


def crear_sesiones_y_transacciones(db, usuarios):
    sesiones_creadas = 0
    tx_creadas = 0
    ahora = datetime.utcnow()

    for u in usuarios:
        perfil = db.query(PerfilComportamiento).filter_by(usuario_id=u.id).first()
        if not perfil:
            continue
        
        dispositivos_h = json.loads(perfil.dispositivos_frecuentes or "[]")
        ubicaciones_h = json.loads(perfil.ubicaciones_habituales or "[]")
        ips_h = json.loads(perfil.ips_habituales or "[]")

        # Sesiones normales (últimos 30 días)
        for _ in range(random.randint(10, 25)):
            dias_atras = random.randint(0, 30)
            hora = random.choice(json.loads(perfil.horarios_habituales or "[9, 14, 18]"))
            fecha = ahora - timedelta(days=dias_atras, hours=random.randint(0, 2), minutes=random.randint(0, 59))
            fecha = fecha.replace(hour=hora)

            sesion = Sesion(
                id=str(uuid.uuid4()),
                usuario_id=u.id,
                fecha_hora=fecha,
                dispositivo_id=random.choice(dispositivos_h) if dispositivos_h else "unknown",
                ubicacion=random.choice(ubicaciones_h) if ubicaciones_h else "Bogotá",
                ip_acceso=random.choice(ips_h) if ips_h else "192.168.1.1",
                duracion_min=random.randint(5, 45),
                tipo_acceso=random.choice(["web", "mobile"]),
                puntaje_anomalia=random.uniform(0.1, 0.5),
                es_anomala=0,
                nivel_riesgo="BAJO",
            )
            db.add(sesion)
            sesiones_creadas += 1

            # Transacciones normales
            for _ in range(random.randint(0, 3)):
                tx = Transaccion(
                    id=str(uuid.uuid4()),
                    usuario_id=u.id,
                    sesion_id=sesion.id,
                    monto=random.uniform(10000, perfil.monto_promedio_tx * 1.5),
                    tipo=random.choice(["PAGO", "TRANSFERENCIA", "RECARGA"]),
                    estado="COMPLETADA",
                    fecha_hora=fecha + timedelta(minutes=random.randint(1, 20)),
                    dispositivo=sesion.dispositivo_id,
                )
                db.add(tx)
                tx_creadas += 1

        # Sesiones ANÓMALAS (2-4 por usuario)
        for _ in range(random.randint(2, 4)):
            dias_atras = random.randint(0, 7)
            hora_anomala = random.choice([1, 2, 3, 4, 22, 23])
            fecha = ahora - timedelta(days=dias_atras, hours=random.randint(0, 1))
            fecha = fecha.replace(hour=hora_anomala)

            nivel = random.choice(["MEDIO", "ALTO", "CRITICO"])
            sesion = Sesion(
                id=str(uuid.uuid4()),
                usuario_id=u.id,
                fecha_hora=fecha,
                dispositivo_id=random.choice(DISPOSITIVOS),  # dispositivo nuevo
                ubicacion=random.choice(UBICACIONES[3:]),      # ubicación inusual
                ip_acceso=random.choice(IPS_SOSPECHOSAS),
                duracion_min=random.randint(1, 10),
                tipo_acceso="web",
                puntaje_anomalia=random.uniform(-0.5, -0.05),
                es_anomala=1,
                nivel_riesgo=nivel,
            )
            db.add(sesion)
            sesiones_creadas += 1

            # Alerta para esta sesión
            factores = []
            if hora_anomala < 5:
                factores.append(f"Acceso en horario inusual ({hora_anomala}:00h)")
            factores.append("IP de acceso inusual")
            factores.append("Dispositivo no reconocido")
            if nivel == "CRITICO":
                factores.append("Monto transaccional 5.2x sobre el promedio")

            alerta = Alerta(
                id=str(uuid.uuid4()),
                usuario_id=u.id,
                sesion_id=sesion.id,
                nivel_riesgo=nivel,
                descripcion=f"Acceso clasificado como riesgo {nivel}. Factores: {', '.join(factores[:2])}.",
                factores=json.dumps(factores),
                puntaje=sesion.puntaje_anomalia,
                estado=random.choice(["NUEVA", "NUEVA", "NUEVA", "RESUELTA", "DESCARTADA"]),
                fecha_creacion=fecha,
            )
            db.add(alerta)

    db.commit()
    print(f"  Sesiones creadas: {sesiones_creadas}")
    print(f"  Transacciones creadas: {tx_creadas}")


def main():
    print("\n🌱 Iniciando seed de datos SIDSID...")
    os.chdir(ROOT_DIR)
    
    init_db()
    db = SessionLocal()

    try:
        print("\n📋 Creando analistas y admins...")
        crear_usuarios_analistas(db)

        print("\n👤 Creando usuarios finales...")
        usuarios = crear_usuarios_finales(db, n=16)

        if not usuarios:
            usuarios = db.query(Usuario).filter_by(rol="usuario").all()

        print("\n🧠 Creando perfiles de comportamiento...")
        crear_perfiles(db, usuarios)

        print("\n📡 Creando sesiones y transacciones...")
        crear_sesiones_y_transacciones(db, usuarios)

        print("\n✅ Seed completado exitosamente!")
        print("\n📌 Credenciales de acceso:")
        print("   Admin:    admin@fintrust.co / sidsid123")
        print("   Analista: analista@fintrust.co / sidsid123")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error en seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
