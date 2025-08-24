"""
module is the repository for grid
"""
from sqlmodel import select

from app.model.db import Grid
from app.repositories.db import get_session


class GridRepository:
    """
    class handles all database requests for grids
    """
    @staticmethod
    def get_all():
        """
        get all grids from database
        """
        with get_session() as session:
            return session.exec(select(Grid)).all()

    @staticmethod
    def get_by_id(grid_id: int):
        """
        get grid from database with specified id
        """
        with get_session() as session:
            return session.get(Grid, grid_id)

    @staticmethod
    def add(grid: Grid):
        """
        add grid to database
        """
        with get_session() as session:
            session.add(grid)
            session.commit()
            session.refresh(grid)
            return grid
