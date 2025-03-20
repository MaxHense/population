from pydantic import BaseModel

class GridDTO(BaseModel):
    name: str
    size: str
    definition: str

class FullGridDTO(GridDTO):
    id: int

    @classmethod
    def from_model(cls, model):
        return cls(
            id=model.id,
            name=model.name,
            size=model.size,
            definition=model.definition,
        )
