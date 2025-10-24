import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Récupère la variable d'environnement DATABASE_URL
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL is not set. Check your Render environment variables.")

# Corrige le format Render si besoin (Render donne souvent postgres:// au lieu de postgresql+psycopg2://)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

# Crée le moteur SQLAlchemy
engine = create_engine(database_url, echo=True)

# Crée la session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour déclarer les modèles
Base = declarative_base()

# Fonction pour créer les tables
def init_db():
    Base.metadata.create_all(bind=engine)
