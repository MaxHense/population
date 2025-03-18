import os

from sqlmodel import Field, SQLModel, UniqueConstraint, Session, create_engine
from typing import Optional
from app.models import GridDTO
from dotenv import load_dotenv

db_url = os.environ['DBURL']

engine = create_engine(db_url, echo=True)

class Grid(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "size", "definition", name="unique_grid"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: str
    definition: str

    @classmethod
    def from_dto(cls, dto: GridDTO):
        grid = cls(
            name=dto.name,
            size=dto.size,
            definition=dto.definition
        )
        with Session(engine) as session:
            session.add(grid)
            session.commit()
            session.refresh(grid)
            return grid
