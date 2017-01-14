"""add_cinemas_table

Revision ID: e6e68fd5007e
Revises:
Create Date: 2017-01-09 20:48:05.974076

"""

from alembic import op
import sqlalchemy as sa


revision = 'e6e68fd5007e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_subscity():
    op.create_table('cinemas',
                    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
                    sa.Column('api_id', sa.String(length=64), nullable=False),
                    sa.Column('city', sa.String(length=64), nullable=False),
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
                    sa.PrimaryKeyConstraint('id', 'api_id', 'name'))

    op.create_table('screenings',
                    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
                    sa.Column('cinema_api_id', sa.String(length=64), nullable=False),
                    sa.Column('movie_api_id', sa.String(length=64), nullable=False),
                    sa.Column('ticket_api_id', sa.String(length=128), nullable=True),
                    sa.Column('city', sa.String(length=64), nullable=False),
                    sa.Column('date_time', sa.DateTime(), nullable=False),
                    sa.Column('price_min', sa.Float(), nullable=True),
                    sa.Column('price_max', sa.Float(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id', 'cinema_api_id', 'movie_api_id')
                    )

    op.create_index('ix_cinemas', 'cinemas', ['api_id', 'city'], unique=False)
    op.create_index('ix_screenings', 'screenings', ['cinema_api_id', 'movie_api_id', 'city',
                                                    'date_time'], unique=False)


def downgrade_subscity():
    op.drop_index('ix_cinemas', table_name='cinemas')
    op.drop_index('ix_screenings', table_name='screenings')
    op.drop_table('cinemas')
    op.drop_table('screenings')
