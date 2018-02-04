from __future__ import with_statement
import logging

from alembic import context
from sqlalchemy import engine_from_config, pool

from subscity.models.base import Base as ModelsBase


DB_NAME = 'subscity'

logger = logging.getLogger('alembic.runtime.migration')
logger.setLevel(logging.INFO)
config = context.config
target_metadata = {DB_NAME: ModelsBase.metadata}


def run_migrations_online():
    # for the direct-to-DB use case, start a transaction on all
    # engines, then run all migrations, then commit all transactions.
    from subscity.main import APP
    from subscity.models.cinema import Cinema
    from subscity.models.screening import Screening
    from subscity.models.movie import Movie

    engines = {DB_NAME: {}}
    engines[DB_NAME]['engine'] = engine_from_config(
        {'sqlalchemy.url': APP.config['SQLALCHEMY_DATABASE_URI']},
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    for name, rec in engines.items():
        engine = rec['engine']
        rec['connection'] = conn = engine.connect()
        rec['transaction'] = conn.begin()

    try:
        for name, rec in engines.items():
            context.configure(
                connection=rec['connection'],
                upgrade_token="%s_upgrades" % name,
                downgrade_token="%s_downgrades" % name,
                target_metadata=target_metadata.get(name)
            )
            context.run_migrations(engine_name=name)

        for rec in engines.values():
            rec['transaction'].commit()
    except:
        for rec in engines.values():
            rec['transaction'].rollback()
        raise
    finally:
        for rec in engines.values():
            rec['connection'].close()


run_migrations_online()
