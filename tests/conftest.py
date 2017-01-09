import os
import pytest

from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy.schema import MetaData, DropConstraint
from sqlalchemy.exc import ProgrammingError

from subscity.main import APP

ALEMBIC_CONFIG = os.path.join(os.path.dirname(__file__), '..', 'alembic.ini')


def apply_migrations():
    config = Config(ALEMBIC_CONFIG)
    upgrade(config, 'head')


@pytest.fixture(scope='session', autouse=True)
def app():
    # Setting up a flask test client
    APP.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
    APP.testing = True
    return APP


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def setup_clean_db(app):
    # Clear out any existing tables
    from subscity.main import DB
    # db_name = os.environ.get('DN_NAME')
    engine = DB.get_engine(APP)
    metadata = MetaData(engine)
    metadata.reflect()
    # for table in metadata.tables.values():
    #     for fk in table.foreign_keys:
    #         engine.execute(DropConstraint(fk.constraint))
    metadata.drop_all()
    apply_migrations()


@pytest.yield_fixture
def dbsession(request, monkeypatch, setup_clean_db):
    from subscity.main import DB
    # Prevent the dbsession from closing (make it a no-op) and
    # committing (redirect to flush() instead)
    session = DB.session
    monkeypatch.setattr(session, 'commit', session.flush)
    monkeypatch.setattr(session, 'remove', lambda: None)
    monkeypatch.setattr(DB.session(), 'close', lambda: None)

    try:
        yield session
    finally:
        # Roll back at the end of every test
        session.rollback()
