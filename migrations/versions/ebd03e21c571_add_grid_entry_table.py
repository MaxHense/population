"""Add Grid Entry Table

Revision ID: ebd03e21c571
Revises: 567e57018e4f
Create Date: 2025-03-19 11:16:08.077436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = 'ebd03e21c571'
down_revision: Union[str, None] = '567e57018e4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_geospatial_table('location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('grid_id', sa.Integer(), nullable=False),
    sa.Column('geom', Geometry(geometry_type='POINT', srid=3035, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.Column('population', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['grid_id'], ['grid.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_geospatial_index('idx_location_geom', 'location', ['geom'], unique=False, postgresql_using='gist', postgresql_ops={})
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_geospatial_index('idx_location_geom', table_name='location', postgresql_using='gist', column_name='geom')
    op.drop_geospatial_table('location')
    # ### end Alembic commands ###
