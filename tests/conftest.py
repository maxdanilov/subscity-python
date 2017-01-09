import os
import pytest

from sqlalchemy.schema import MetaData, DropConstraint
from sqlalchemy.exc import ProgrammingError

from subscity.main import APP


@pytest.fixture(scope='session', autouse=True)
def app():
    # Setting up a flask test client
    APP.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
    # APP.config['SQLALCHEMY_BINDS'] = {'subscity-test': os.environ.get('DB_URI')}
    APP.testing = True
    return APP


@pytest.fixture(scope='session')
def setup_clean_db(app):
    # Clear out any existing tables
    from subscity.main import DB
    # db_name = os.environ.get('DN_NAME')
    engine = DB.get_engine(APP)
    metadata = MetaData(engine)
    metadata.reflect()
    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            try:
                engine.execute(DropConstraint(fk.constraint))
            except ProgrammingError:
                pass
    metadata.drop_all()


@pytest.fixture(scope='session')
def setup_create_db(app):
    from subscity.main import DB
    # db_name = os.environ.get('DB_NAME')
    engine = DB.get_engine(APP)
    from subscity.models.cinema import Cinema
    Cinema.__table__.create(engine)


@pytest.yield_fixture
def dbsession(request, monkeypatch, setup_clean_db, setup_create_db):
    from subscity.main import DB
    # Prevent the setup_smartb_dbsession from closing (make it a no-op) and
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
