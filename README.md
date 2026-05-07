# SIDSID — Sistema Inteligente de Detección de Suplantación de Identidad Digital

**FinTrust Digital Services S.A.S.**  
Ingeniería de Software — 2025/2026  
Equipo: Torres Ortega · Cuello Haydar · Castellón García

---

## Descripción

SIDSID es un prototipo funcional de sistema de detección de anomalías en comportamiento digital de usuarios de una plataforma fintech. Analiza patrones de acceso en tiempo real usando **Isolation Forest** y genera alertas clasificadas por nivel de riesgo (BAJO / MEDIO / ALTO / CRÍTICO) para su revisión por analistas de seguridad.

## Arquitectura

```
SIDSID/
├── backend/          # API REST — Flask + SQLAlchemy
│   ├── config/       # Configuración, BD
│   ├── models/       # Modelos SQLAlchemy (ORM)
│   ├── routes/       # Endpoints REST
│   ├── services/     # Lógica de negocio
│   ├── scripts/      # Seed de datos
│   └── tests/        # Tests de endpoints
├── ia/               # Módulo de Inteligencia Artificial
│   ├── features.py   # Feature engineering (8 features)
│   ├── train.py      # Entrenamiento Isolation Forest
│   ├── evaluar.py    # Clasificación de sesiones
│   ├── modelo.pkl    # Modelo entrenado
│   └── tests/        # Tests del modelo
└── frontend/         # SPA React — Tailwind CSS
    ├── pages/        # Login, Dashboard, Alertas, Usuarios
    ├── components/   # Navbar, KpiCard, AlertaRow, etc.
    ├── hooks/        # useAlertas, useMetricas
    └── services/     # Llamadas a la API
```

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + Tailwind CSS + Recharts |
| Backend | Python 3.11 + Flask + Flask-JWT-Extended |
| ORM | SQLAlchemy |
| Base de datos | SQLite (desarrollo) |
| IA/ML | Scikit-learn — Isolation Forest |
| Datos | Pandas + NumPy |

## Requisitos

- Python 3.11+
- Node.js 18+

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/sidsid-fintrust.git
cd sidsid-fintrust
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt

# Crear archivo .env (ver .env.example)
cp .env.example .env
```

### 3. Entrenar el modelo de IA

```bash
cd ..  # desde la raíz del proyecto
python -m ia.train
```

### 4. Poblar la base de datos

```bash
python -m backend.scripts.seed_data
```

### 5. Iniciar el backend

```bash
python backend/app.py
# Disponible en http://localhost:5000
```

### 6. Frontend

```bash
cd frontend
npm install
npm run dev
# Disponible en http://localhost:3000
```

## Credenciales de acceso (demo)

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Admin | admin@fintrust.co | sidsid123 |
| Analista | analista@fintrust.co | sidsid123 |

## API REST — Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login` | Autenticación JWT |
| GET | `/api/auth/me` | Perfil del usuario autenticado |
| POST | `/api/sesiones` | Registrar sesión + análisis IA automático |
| GET | `/api/sesiones` | Listar sesiones |
| GET | `/api/alertas` | Listar alertas (con filtros) |
| GET | `/api/alertas/{id}` | Detalle de alerta |
| PUT | `/api/alertas/{id}/resolver` | Resolver o descartar alerta |
| GET | `/api/alertas/resumen` | Conteo de alertas por nivel |
| GET | `/api/usuarios` | Listar usuarios |
| GET | `/api/usuarios/{id}/perfil` | Perfil de comportamiento |
| POST | `/api/usuarios/{id}/bloquear` | Bloquear cuenta |
| GET | `/api/metricas` | KPIs del sistema + métricas del modelo |
| POST | `/api/analizar` | Análisis directo de anomalía |

## Features del modelo de IA

El modelo Isolation Forest analiza 8 variables por sesión:

| Feature | Tipo | Descripción |
|---------|------|-------------|
| `hora_del_dia` | Numérica | Hora del acceso (0–23) |
| `dia_semana` | Numérica | Día (0=lunes, 6=domingo) |
| `dispositivo_nuevo` | Binaria | Dispositivo no habitual |
| `distancia_geo_aprox` | Numérica | Ubicación vs. historial |
| `sesiones_24h` | Numérica | Sesiones en las últimas 24h |
| `monto_relativo` | Numérica | Monto / promedio histórico |
| `frecuencia_tx_sesion` | Numérica | Transacciones en la sesión |
| `ip_nueva` | Binaria | IP no habitual |

## Métricas del modelo

| Métrica | Valor |
|---------|-------|
| Precisión | ~86% |
| Recall | ~100% |
| F1-Score | ~92% |
| FPR | ~15% |

## Tests

```bash
# Tests del backend
pip install pytest
python -m pytest backend/tests/test_endpoints.py -v

# Tests del módulo IA
python -m pytest ia/tests/test_modelo.py -v
```

## Consideraciones éticas

- **Privacidad por diseño**: Solo se recopilan los datos mínimos necesarios para el análisis.
- **Control humano**: Ningún bloqueo se ejecuta de forma automática; siempre existe revisión humana.
- **Transparencia**: Cada alerta indica los factores que generaron la clasificación.
- **Cumplimiento**: Compatible con Ley 1581 de 2012 (Protección de Datos — Colombia).
- **Datos simulados**: Todos los datos son ficticios; ningún dato real de usuarios es utilizado.

---

*Documentación arquitectónica completa disponible en `arc42.pdf`*
