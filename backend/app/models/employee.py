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
