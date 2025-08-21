from app.repositories.grid import GridRepository
from app.models import GridDTO
from app.model import Grid

class GridService:
    @staticmethod
    def list_grids():
        return GridRepository.get_all()
    
    @staticmethod
    def get_by_id(grid_id: int):
        return GridRepository.get_by_id(grid_id)
    
    @staticmethod
    def set_new_grid(gridDTO: GridDTO):
        grid = Grid.from_dto(gridDTO)
        return GridRepository.add(grid)