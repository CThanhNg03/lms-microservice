from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel

from app.setting.setting import logger 

def get_annotations(dataclass_type: type):
    annotations = {}
    if dataclass_type.__name__ == "Optional":
        return get_annotations(dataclass_type.__args__[0])
    if hasattr(dataclass_type, "__bases__"):
        for base in dataclass_type.__bases__:
            annotations.update(get_annotations(base))
    if hasattr(dataclass_type, "__annotations__"):
        annotations.update(dataclass_type.__annotations__)
    return annotations

def pydantic_to_dataclass(pyd_obj, dataclass_type: type):
    if dataclass_type.__name__ == "Optional":
        dataclass_type = dataclass_type.__args__[0]
    if isinstance(pyd_obj, BaseModel):
        return pydantic_to_dataclass(pyd_obj.model_dump(), dataclass_type)
    
    if isinstance(pyd_obj, dict):
        annotations = get_annotations(dataclass_type)
        field_values = {
            key: pydantic_to_dataclass(value, annotations[key])
            for key, value in pyd_obj.items()
        }
        return dataclass_type(**field_values)
    elif isinstance(pyd_obj, (list, List)):

        return [pydantic_to_dataclass(item, dataclass_type.__args__[0]) for item in pyd_obj]
    return pyd_obj

def object_to_dict(obj):
    if isinstance(obj, dict):
        return {key: object_to_dict(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [object_to_dict(item) for item in obj]
    if hasattr(obj, "__dict__"):
        return {key: object_to_dict(value) for key, value in obj.__dict__.items()}
    return obj

if __name__ == "__main__":
    @dataclass
    class TestModel:
        a: int
        b: str

    @dataclass
    class TestModel2:
        e: int
        f: str
    
    @dataclass
    class TestModel3:
        g: int
        j: List[TestModel2]
        h: Optional[TestModel]

    @dataclass
    class TestModel4(TestModel3):
        k: bool

    data = {
        "g": 1,
        # "h": {
        #     "a": 2,
        #     "b": "test"
        # },
        "h": None,
        "j": [
            {
                "e": 3,
                "f": "test2"
            },
            {
                "e": 4,
                "f": "test3"
            }
        ],
        "k": True
    }
    

    # print(get_annotations(TestModel4))
    print(pydantic_to_dataclass(data, TestModel4))
    print(object_to_dict(pydantic_to_dataclass(data, TestModel4)))