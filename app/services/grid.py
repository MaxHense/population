from app.repositories.grid import GridRepository

class GridService:
    @staticmethod
    def list_grids():
        return GridRepository.get_all()