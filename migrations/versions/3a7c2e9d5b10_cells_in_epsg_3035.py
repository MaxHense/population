"""All cells in EPSG:3035, cell size in metres

One query covers every grid: cells of all grids share one CRS, the grid keeps
the CRS of its source data (srid) and its cell size for drawing the squares.

Revision ID: 3a7c2e9d5b10
Revises: fe1e4608e178
Create Date: 2026-11-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '3a7c2e9d5b10'
down_revision: Union[str, None] = 'fe1e4608e178'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('grid', sa.Column('cell_size_m', sa.Integer(), nullable=True))
    # '1km' -> 1000, '100m' -> 100
    op.execute("UPDATE grid SET cell_size_m = round(substring(size from '[0-9.]+')::numeric"
               " * CASE WHEN size ~* 'km' THEN 1000 ELSE 1 END)")
    op.alter_column('grid', 'cell_size_m', nullable=False)
    op.create_check_constraint('cell_size_positive', 'grid', 'cell_size_m > 0')
    op.drop_constraint('unique_grid', 'grid', type_='unique')
    op.drop_column('grid', 'size')
    op.create_unique_constraint('unique_grid_name', 'grid', ['name'])
    op.execute("ALTER TABLE location ALTER COLUMN geom TYPE geometry(Point, 3035)"
               " USING ST_Transform(geom, 3035)")


def downgrade() -> None:
    op.execute("ALTER TABLE location ALTER COLUMN geom TYPE geometry(Point)")
    op.drop_constraint('unique_grid_name', 'grid', type_='unique')
    op.add_column('grid', sa.Column('size', sa.String(), nullable=True))
    op.execute("UPDATE grid SET size = cell_size_m || 'm'")
    op.alter_column('grid', 'size', nullable=False)
    op.drop_constraint('cell_size_positive', 'grid', type_='check')
    op.drop_column('grid', 'cell_size_m')
    op.create_unique_constraint('unique_grid', 'grid', ['name', 'size', 'srid'])
