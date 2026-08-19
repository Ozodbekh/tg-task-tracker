from pydantic import BaseModel

from app.models.stats import StatusCounts


class EmployeeDigest(BaseModel):
    telegram_id: int
    name: str
    total: int
    by_status: StatusCounts
