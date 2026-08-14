from pydantic import ValidationError
from starlette.requests import Request

from app.models.filters import TaskFilters
from app.models.page import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, Pagination

DEFAULT_SORT = "-created_at"
ALLOWED_SORTS = frozenset({"created_at", "-created_at", "done_at", "-done_at"})


class FilterError(Exception):
    pass


def parse_filters(request: Request) -> TaskFilters:
    query = request.query_params
    payload = {
        "period": query.get("period"),
        "bucket": query.get("bucket"),
        "status": query.get("status"),
        "chat_id": query.get("chat_id"),
        "chat_type": query.get("chat_type"),
        "employee_id": query.get("employee_id"),
    }
    try:
        return TaskFilters(**{k: v for k, v in payload.items() if v is not None})
    except ValidationError as error:
        raise FilterError from error


def parse_pagination(request: Request) -> Pagination:
    query = request.query_params
    try:
        page = int(query.get("page", 1))
        page_size = int(query.get("page_size", DEFAULT_PAGE_SIZE))
    except ValueError as error:
        raise FilterError from error

    if page < 1 or page_size < 1:
        raise FilterError
    return Pagination(page=page, page_size=min(page_size, MAX_PAGE_SIZE))


def parse_sort(request: Request) -> str:
    sort = request.query_params.get("sort", DEFAULT_SORT)
    if sort not in ALLOWED_SORTS:
        raise FilterError
    return sort
