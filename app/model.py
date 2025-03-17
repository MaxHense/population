from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint

class Grid(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "size", "definition", name="unique_grid"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: str
    definition: str