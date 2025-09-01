from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

# Minimal finance models - to be expanded later

class FinanceBase(SQLModel):
    pass

class Finance(FinanceBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    # Add specific fields as needed