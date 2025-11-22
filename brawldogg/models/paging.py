from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Cursor(BaseModel):
    after: str | None = None
    before: str | None = None


class Paging(BaseModel):
    cursors: Cursor


class PagingResponse(BaseModel, Generic[T]):
    items: list[T]
    paging: Paging
