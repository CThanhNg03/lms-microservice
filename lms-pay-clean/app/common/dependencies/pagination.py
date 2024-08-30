from typing import Annotated

from fastapi import Depends


async def pagination_params(page: int = 1, limit: int = 10, skip: int = 0):
    return {
        "page": page,
        "limit": limit,
        "skip": skip
    }

PaginDep = Annotated[dict, Depends(pagination_params)]
