from sqlalchemy import Select

from app.model.pagination import PaginationParamsModel


def paginate(q: Select, pagin: PaginationParamsModel) -> Select:
    return q.offset((pagin.page - 1) * pagin.limit + pagin.skip).limit(pagin.limit)