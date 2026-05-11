"""
Guarda el vector de features de una sesión en datos_entrenamiento_ia.
Desacoplado del route para facilitar pruebas unitarias.
"""
from config.database import db
from models.entrenamiento import DatoEntrenamientoIA


def guardar_features(sesion, resultado: dict) -> None:
    """
    Calcula y persiste los features derivados del análisis de la sesión.
    No hace commit — el caller maneja la transacción.
    """
    # Evitar duplicados (unique constraint en sesion_id)
    existente = DatoEntrenamientoIA.query.filter_by(sesion_id=sesion.id).first()
    if existente:
        existente.puntaje_asignado = resultado["puntaje"]
        return

    hora  = sesion.hora_inicio.hour if sesion.hora_inicio else 12
    minuto= sesion.hora_inicio.minute if sesion.hora_inicio else 0
    hora_norm = round((hora * 60 + minuto) / 1439, 4)

    # Datos del perfil del usuario
    perfil = sesion.usuario.perfil if sesion.usuario else None
    ips_conocidas  = (perfil.ips_habituales or []) if perfil else []
    devs_conocidos = (perfil.dispositivos_habituales or []) if perfil else []
    umbral_monto   = float(perfil.umbral_monto or 0) if perfil else 0.0

    # Transacciones de la sesión
    txs          = list(sesion.transacciones)
    num_txn      = len(txs)
    monto_maximo = max((float(t.monto) for t in txs), default=0.0)

    dato = DatoEntrenamientoIA(
        sesion_id                = sesion.id,
        hora_normalizada         = hora_norm,
        dia_semana               = sesion.hora_inicio.weekday() if sesion.hora_inicio else 0,
        frecuencia_acceso_7d     = 0,   # TODO: calcular con query real
        intentos_fallidos_24h    = 0,   # TODO: calcular con query real
        dispositivo_conocido     = (sesion.dispositivo in devs_conocidos) if sesion.dispositivo else False,
        ip_conocida              = (sesion.ip in ips_conocidas) if sesion.ip else False,
        distancia_geo_km         = 0.0,  # TODO: calcular con haversine
        monto_promedio_historico = umbral_monto,
        num_transacciones_sesion = num_txn,
        monto_maximo_sesion      = monto_maximo,
        puntaje_asignado         = resultado["puntaje"],
        etiqueta_fraude          = None,   # se actualiza cuando analista cierra la alerta
    )
    db.session.add(dato)
