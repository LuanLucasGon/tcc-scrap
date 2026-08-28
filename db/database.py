import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

Base = declarative_base()


def get_database_url() -> str:
    user = os.getenv("POSTGRES_USER", "tcc")
    password = os.getenv("POSTGRES_PASSWORD", "tcc")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    name = os.getenv("POSTGRES_DB", "projectTCC")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


engine = create_engine(get_database_url(), future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
