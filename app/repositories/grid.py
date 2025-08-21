from sqlmodel import select
from app.model import Grid
from app.db import get_session

class GridRepository:
    @staticmethod
    def get_all():
        with get_session() as session:
            return session.exec(select(Grid)).all()

    @staticmethod
    def get_by_id(grid_id: int):
        with get_session() as session:
            return session.get(Grid, grid_id)
    
    @staticmethod
    def add(grid: Grid):
        with get_session() as session:
            session.add(grid)
            session.commit()
            session.refresh(grid)
            return grid