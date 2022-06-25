import uuid
from http import HTTPStatus
from typing import Dict
from typing import List
from typing import Union, Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel, Field
from services.film import FilmService
from services.film import get_film_service

router = APIRouter()


FILM_ERROR_NO_ITEM_FOR_REQUEST = 'No films found based on your request'
FILM_ERROR_ITEM_NOT_FOUND = 'The film is not found'
FILM_ERROR_NO_SIMILAR_FILM = 'No similar films found'
FILM_ERROR_WRONG_SORT_PARAMETER = 'Wrong sort parameter'


class UUIDModel(BaseModel):
    uuid: uuid.UUID


class GenreInFilm(UUIDModel):
    name: str


class PersonInFilm(UUIDModel):
    full_name: str


class Film(UUIDModel):
    title: str
    imdb_rating: Union[float, None]
    description: str | None = Field(default='')
    genre: List[GenreInFilm]
    directors: List[PersonInFilm]
    actors: List[PersonInFilm]
    writers: List[PersonInFilm]


class FilmOut(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: Union[float, None]


@router.get('/search', summary='Search filmwork with words in detailed information')
async def film_search(
    q: str = Query(None, alias='query'),
    page: int = Query(1, alias='page[number]'),
    size: int = Query(50, alias='page[size]'),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmOut]:
    """
    Return a list of filmworks with words in detailed information.

    Query parameters:
    - **query** - search phrase or word.

    Parameters of pagination:
    - **page[size]**: the number of elements per page.
    - **page[number]**: the number of the current page.
    """
    films = await film_service.search_objects(q, 'Film', page, size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_ERROR_NO_ITEM_FOR_REQUEST)
    return [FilmOut(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@router.get('/{film_id}', response_model=Film, summary='Get detailed information about one filmwork.')
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    """
    Return detailed information about one filmwork.

    - **film_id**: uuid of filmwork.
    """
    film = await film_service.get_by_id(film_id, 'Film')
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_ERROR_ITEM_NOT_FOUND)

    return film


@router.get('/', summary='Get a list of all filmworks.')
async def films_list(
    sort_by: str = Query(None, alias='sort'),
    filter_by: str = Query(None, alias='filter[genre]'),
    page: int = Query(1, alias='page[number]'),
    size: int = Query(50, alias='page[size]'),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmOut]:
    """
    Return a list of filmworks with pagination.

    Parameters of pagination:
    - **page[size]**: the number of elements per page.
    - **page[number]**: the number of the current page.

    Other parameters:
    - **sort**: Sort items by parameter. If start with '-' is descending order.
    - **filter[genre]**: Return filmworks only these genres.
    """
    # check sort params
    if sort_by and sort_by.replace('-', '') not in ['imdb_rating']:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=FILM_ERROR_WRONG_SORT_PARAMETER)
    films = await film_service.get_all_films(sort_by, filter_by, page, size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_ERROR_NO_ITEM_FOR_REQUEST)
    return [FilmOut(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


# TODO pagination
@router.get('/{film_id}/similar', summary='Get list of similar filmworks')
async def similar_films_search(
    film_id: str,
    page: int = Query(1, alias='page[number]'),
    size: int = Query(50, alias='page[size]'),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmOut]:
    """
    Return a list of similar filmworks of specified filmwork.

    Parameters:
    - **film_id**: uuid of filmwork.

    Parameters of pagination:
    - **page[size]**: the number of elements per page.
    - **page[number]**: the number of the current page.
    """
    films = await film_service.get_similar_films(film_id, page, size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_ERROR_NO_SIMILAR_FILM)
    return [FilmOut(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]
