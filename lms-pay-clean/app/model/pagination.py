from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")

@dataclass
class PaginationParamsModel:
    page: int
    limit: int
    skip: int

@dataclass
class PaginationModel(Generic[T], PaginationParamsModel):
    total: int
    items: List[T]
