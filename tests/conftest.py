import socket

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from infra.database import Base, get_database_url

# Import every entity so its table is registered on Base.metadata before create_all.
from subject.entity.subject import Subject  # noqa: F401
from question.entity.question import Question  # noqa: F401
from topic.entity.topic import Topic  # noqa: F401


def _database_reachable(url: str) -> bool:
    try:
        _, _, hostpart = url.partition("@")
        host, _, portpart = hostpart.partition("/")[0].partition(":")
        port = int(portpart or "5432")
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def db_engine():
    url = get_database_url()
    if not _database_reachable(url):
        pytest.skip(
            "Postgres indisponível — rode `docker compose up -d db` "
            "para os testes de integração"
        )
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Session isolada: tudo é revertido no fim do teste."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
