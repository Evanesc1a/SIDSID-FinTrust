from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_DB_URL = f"sqlite:///{os.path.join(_BACKEND_DIR, 'sidsid.db')}"
DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_DB_URL)

# Resolve relative sqlite paths to absolute (skip :memory: and already-absolute paths)
if DATABASE_URL.startswith("sqlite:///"):
    _db_path = DATABASE_URL[len("sqlite:///"):]
    if _db_path != ":memory:" and not os.path.isabs(_db_path):
        DATABASE_URL = f"sqlite:///{os.path.join(_BACKEND_DIR, _db_path)}"

_is_memory = DATABASE_URL == "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    **({"poolclass": StaticPool} if _is_memory else {}),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.models import usuario, sesion, perfil, alerta, transaccion
    Base.metadata.create_all(bind=engine)
