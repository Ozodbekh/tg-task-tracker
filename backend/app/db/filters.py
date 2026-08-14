from app.models.filters import DateRange, TaskFilters

TASK_SOURCE = "tasks t JOIN chats c ON c.id = t.chat_id"
UNRESOLVED_SOURCE = "unresolved_messages u JOIN chats c ON c.id = u.chat_id"


class FilterClause:
    def __init__(self, sql: str, parameters: list[object]) -> None:
        self.sql = sql
        self.parameters = parameters


def _range_conditions(column: str, window: DateRange) -> tuple[list[str], list[object]]:
    conditions = [f"datetime({column}) < datetime(?)"]
    parameters: list[object] = [window.end.isoformat()]
    if window.start is not None:
        conditions.insert(0, f"datetime({column}) >= datetime(?)")
        parameters.insert(0, window.start.isoformat())
    return conditions, parameters


def task_clause(filters: TaskFilters, window: DateRange) -> FilterClause:
    conditions, parameters = _range_conditions("t.created_at", window)

    if filters.status is not None:
        conditions.append("t.status = ?")
        parameters.append(filters.status)
    if filters.chat_id is not None:
        conditions.append("t.chat_id = ?")
        parameters.append(filters.chat_id)
    if filters.chat_type is not None:
        conditions.append("c.type = ?")
        parameters.append(filters.chat_type)
    if filters.employee_id is not None:
        conditions.append("t.employee_id = ?")
        parameters.append(filters.employee_id)

    return FilterClause(" AND ".join(conditions), parameters)


def unresolved_clause(filters: TaskFilters, window: DateRange) -> FilterClause:
    conditions, parameters = _range_conditions("u.created_at", window)

    if filters.chat_id is not None:
        conditions.append("u.chat_id = ?")
        parameters.append(filters.chat_id)
    if filters.chat_type is not None:
        conditions.append("c.type = ?")
        parameters.append(filters.chat_type)

    return FilterClause(" AND ".join(conditions), parameters)
