import abc
from typing import List, Optional

from app.model.admin import AdminModel, CreateAdminModel, GetAdminParamsModel
from app.repositories.abstraction.abstract import AbstractRepository


class AbstractAdminRepository(AbstractRepository):

    @abc.abstractmethod
    async def get_user(self, id: int) -> AdminModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def list_user(self, params: Optional[GetAdminParamsModel]) -> List[AdminModel]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_user(self, user: CreateAdminModel) -> AdminModel:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_user(self, id: int, user: CreateAdminModel) -> AdminModel:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_user(self, id: int) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def find_user(self, usernameOrEmail: str) -> AdminModel | None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def deactivate_user(self, id: int) -> AdminModel:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def activate_user(self, id: int) -> AdminModel:
        raise NotImplementedError

