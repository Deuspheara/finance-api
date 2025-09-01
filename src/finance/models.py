from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

# Minimal finance models - to be expanded later

class FinanceBase(SQLModel):
    pass

class Finance(FinanceBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    # Add specific fields as needed
