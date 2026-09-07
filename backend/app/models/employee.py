from datetime import datetime

from pydantic import BaseModel


class EmployeeIdentity(BaseModel):
    telegram_id: int
    name: str


class Employee(BaseModel):
    id: int
    telegram_id: int
    name: str
    created_at: datetime
    left_at: datetime | None = None

    @property
    def active(self) -> bool:
        return self.left_at is None
