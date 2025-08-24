"""
module holds class of GridService, which handles all grid related business logic
"""
from app.repositories.grid import GridRepository
from app.model.dto import GridDTO
from app.model.db import Grid

class GridService:
    """
    this class is the service for grids
    """
    @staticmethod
    def list_grids():
        """
        list all grids of database
        """
        return GridRepository.get_all()

    @staticmethod
    def get_by_id(grid_id: int):
        """
        gets a grid from database with specific id
        """
        return GridRepository.get_by_id(grid_id)

    @staticmethod
    def set_new_grid(grid_dto: GridDTO):
        """
        sets a new grid in database
        """
        grid = Grid.from_dto(grid_dto)
        return GridRepository.add(grid)
