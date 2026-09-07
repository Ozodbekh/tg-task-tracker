from pydantic import BaseModel

from app.models.employee import Employee


class Retirement(BaseModel):
    employee: Employee
    cancelled_tasks: int
