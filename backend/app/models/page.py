from pydantic import BaseModel

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20


class Pagination(BaseModel):
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
