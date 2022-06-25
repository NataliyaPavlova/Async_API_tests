from enum import Enum
from typing import List

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    class PersonType(str, Enum):
        actor = 'actor'
        director = 'director'
        writer = 'writer'

    uuid: str
    full_name: str
    film_ids: List[str]
    role: PersonType | None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        use_enum_values = True
