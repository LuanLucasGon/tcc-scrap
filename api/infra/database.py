import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()


def get_database_url() -> str:
    """Monta a URL de conexão do Postgres a partir das env vars.

    Mesma tabela de variáveis usada pelo scraper (POSTGRES_*), lidas do
    ``.env`` compartilhado na raiz do monorepo.
    """
    user = os.getenv("POSTGRES_USER", "tcc")
    password = os.getenv("POSTGRES_PASSWORD", "tcc")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    name = os.getenv("POSTGRES_DB", "projectTCC")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


engine = create_engine(get_database_url(), future=True)
