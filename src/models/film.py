from typing import List

import orjson
import uuid as uuid
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class UUIDModel(BaseModel):
    uuid: str


class GenreInFilm(UUIDModel):
    name: str


class PersonInFilm(UUIDModel):
    full_name: str


class Film(UUIDModel):
    title: str
    imdb_rating: float | None
    description: str | None
    genre: List[GenreInFilm]
    directors: List[PersonInFilm]
    actors: List[PersonInFilm]
    writers: List[PersonInFilm]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
