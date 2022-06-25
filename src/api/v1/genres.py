import uuid
from http import HTTPStatus
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel
from services.genre import GenreService
from services.genre import get_genre_service

from .films import FilmOut

router = APIRouter()

GENRE_ERROR_NO_ITEM = 'No genres found'
GENRE_ERROR_ITEM_NOT_FOUND = 'The genre is not found'
GENRE_ERROR_NO_POPULAR_FILMS = 'No popular films for the genre'


class Genre(BaseModel):
    uuid: uuid.UUID
    name: str
    description: str
    popularity: int


@router.get('/', summary='Get a list of all genres.')
async def get_genres(
    page: int = Query(1, alias='page[number]'),
    size: int = Query(50, alias='page[size]'),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[Genre]:
    """
    Return a list of genres with pagination.

    Parameters of pagination:
    - **page[size]**: the number of elements per page.
    - **page[number]**: the number of the current page.
    """
    genres = await genre_service.get_genres(page, size)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_ERROR_NO_ITEM)
    return [
        Genre(uuid=genre.uuid, name=genre.name, description=genre.description, popularity=genre.popularity)
        for genre in genres
    ]


@router.get('/{genre_id}', response_model=Genre, summary='Get detailed information about one genre.')
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    """
    Return detailed information about one genre.

    - **genre_id**: uuid of genre.
    """
    genre = await genre_service.get_by_id(genre_id, 'Genre')
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_ERROR_ITEM_NOT_FOUND)

    return Genre(uuid=genre.uuid, name=genre.name, description=genre.description, popularity=genre.popularity)


@router.get('/{genre_id}/popular', summary='Get most popular filmworks of specified genre.')
async def genre_details_popular(
    genre_id: str,
    page: int = Query(1, alias='page[number]'),
    size: int = Query(50, alias='page[size]'),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[FilmOut]:
    """
    Return a list of most popular filmworks of specified genre.

    Parameters of pagination:
    - **page[size]**: the number of elements per page.
    - **page[number]**: the number of the current page.
    """
    films = await genre_service.get_films_by_id(genre_id, page, size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_ERROR_NO_POPULAR_FILMS)

    return [FilmOut(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]
