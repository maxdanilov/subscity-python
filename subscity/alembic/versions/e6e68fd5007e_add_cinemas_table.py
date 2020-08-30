"""add_cinemas_table

Revision ID: e6e68fd5007e
Revises:
Create Date: 2017-01-09 20:48:05.974076

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

revision = 'e6e68fd5007e'
down_revision = None
branch_labels = None
depends_on = None

CINEMAS_TABLE_NAME = 'cinemas-v2'
MOVIES_TABLE_NAME = 'movies-v2'
SCREENINGS_TABLE_NAME = 'screenings-v2'


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_subscity():
    op.create_table(CINEMAS_TABLE_NAME,
                    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
                    sa.Column('api_id', sa.String(length=64), nullable=False),
                    sa.Column('city', sa.String(length=64), nullable=False),
                    sa.Column('city_id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('address', sa.String(length=512), nullable=True),
                    sa.Column('metro', sa.String(length=255), nullable=True),
                    sa.Column('url', sa.String(length=255), nullable=True),
                    sa.Column('phone', sa.String(length=255), nullable=True),
                    sa.Column('fetch_all', sa.Boolean(), nullable=False),
                    sa.Column('latitude', sa.DECIMAL(11, 8), nullable=True),
                    sa.Column('longitude', sa.DECIMAL(11, 8), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id', 'api_id', 'name'),
                    sa.UniqueConstraint('api_id')
                    )

    op.create_table(MOVIES_TABLE_NAME,
                    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
                    sa.Column('api_id', sa.String(length=64), nullable=False),
                    sa.Column('active', sa.Boolean, default=False),
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('title_original', sa.String(length=255), nullable=True),
                    sa.Column('languages', sa.String(length=255), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('description_english', sa.Text(), nullable=True),
                    sa.Column('director', sa.String(length=255), nullable=True),
                    sa.Column('cast', sa.String(length=512), nullable=True),
                    sa.Column('age_restriction', sa.Integer, nullable=True),
                    sa.Column('country', sa.String(length=255), nullable=True),
                    sa.Column('year', sa.Integer, nullable=True),
                    sa.Column('genres', sa.String(length=255), nullable=True),
                    sa.Column('poster', sa.String(length=512), nullable=True),
                    sa.Column('duration', sa.Integer, nullable=True),
                    sa.Column('kinopoisk_id', sa.Integer, nullable=True),
                    sa.Column('imdb_id', sa.Integer, nullable=True),
                    sa.Column('trailer', sa.String(length=255), nullable=True),
                    sa.Column('fetch_mode', sa.SmallInteger, default=0,
                              nullable=False),  # legacy: for compatibility with v1
                    sa.Column('premiere', sa.DateTime(), nullable=True),
                    sa.Column('hide', sa.Boolean, nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('api_id')
                    )

    op.create_table(SCREENINGS_TABLE_NAME,
                    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
                    sa.Column('cinema_api_id', sa.String(length=64),
                              ForeignKey(f'{CINEMAS_TABLE_NAME}.api_id')),
                    sa.Column('movie_api_id', sa.String(length=64),
                              ForeignKey(f'{MOVIES_TABLE_NAME}.api_id')),
                    sa.Column('ticket_api_id', sa.String(length=128), nullable=True),
                    sa.Column('city', sa.String(length=64), nullable=False),
                    sa.Column('date_time', sa.DateTime(), nullable=False),
                    sa.Column('price_min', sa.Integer(), nullable=True),
                    sa.Column('price_max', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_index('ix_movies', MOVIES_TABLE_NAME, ['api_id'], unique=False)
    op.create_index('ix_cinemas', CINEMAS_TABLE_NAME, ['api_id', 'city'], unique=False)
    op.create_index('ix_screenings', SCREENINGS_TABLE_NAME, ['city', 'cinema_api_id'], unique=False)
    op.create_index('ix_screenings2', SCREENINGS_TABLE_NAME, ['city', 'movie_api_id'], unique=False)


def downgrade_subscity():
    op.drop_index('ix_movies', table_name=MOVIES_TABLE_NAME)
    op.drop_index('ix_cinemas', table_name=CINEMAS_TABLE_NAME)
    op.drop_index('ix_screenings2', table_name=SCREENINGS_TABLE_NAME)
    op.drop_index('ix_screenings', table_name=SCREENINGS_TABLE_NAME)
    op.drop_table(SCREENINGS_TABLE_NAME)
    op.drop_table(CINEMAS_TABLE_NAME)
    op.drop_table(MOVIES_TABLE_NAME)
