from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase

class Base(MappedAsDataclass, DeclarativeBase):
    def asDataClass(self):
        pass
    ...
