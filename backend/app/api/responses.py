from collections.abc import Sequence

from pydantic import BaseModel
from starlette.responses import JSONResponse


def model(payload: BaseModel, status_code: int = 200) -> JSONResponse:
    return JSONResponse(payload.model_dump(mode="json"), status_code=status_code)


def models(payload: Sequence[BaseModel]) -> JSONResponse:
    return JSONResponse([item.model_dump(mode="json") for item in payload])


def not_found() -> JSONResponse:
    return JSONResponse({"detail": "Not found"}, status_code=404)


def invalid_filters() -> JSONResponse:
    return JSONResponse({"detail": "Invalid filters"}, status_code=400)
