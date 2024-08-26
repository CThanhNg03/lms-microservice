import abc


class AbstractRepository(abc.ABC):
    session: any

    @abc.abstractmethod()
    async def create(self, **kwargs):
        ...

    @abc.abstractmethod()
    async def read(self, **kwargs):
        ...

    @abc.abstractmethod()
    async def update(self, **kwargs):
        ...

    @abc.abstractmethod()
    async def delete(self, **kwargs):
        ...
