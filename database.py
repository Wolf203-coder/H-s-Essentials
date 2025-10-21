# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

MYSQL_USER = "root"
MYSQL_PASSWORD = ""  
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DB = "clean_company"

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db(drop_all=False):
    """Initialise la base. Si drop_all=True, toutes les tables sont supprimées avant d’être recréées."""
    import models  # importe les modèles avant création
    if drop_all:
        print("⚠️ Suppression de toutes les tables existantes...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès !")
