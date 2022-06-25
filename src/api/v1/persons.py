import uuid
from http import HTTPStatus
from typing import List

from fastapi import APIRouter
from fastapi import Depends, Query
from fastapi import HTTPException
from pydantic import BaseModel
from services.person import PersonService
from services.person import get_person_service
from .films import FilmOut

router = APIRouter()

PERSON_ERROR_NO_ITEM = 'No persons found'
PERSON_ERROR_ITEM_NOT_FOUND = 'The person is not found'
PERSON_ERROR_FILMS_NOT_FOUND = 'No films found for this person'


class Person(BaseModel):
    uuid: uuid.UUID
    full_name: str
    role: str | None
    film_ids: List[str]


@router.get('/search')
async def search_persons(
    q: str = Query(None, alias='query'),
    page: int = Query(1, alias='page[number]'),
    size: int = Query(50, alias='page[size]'),
    person_service: PersonService = Depends(get_person_service),
) -> List[Person]:
    persons = await person_service.search_objects(q, 'Person', page, size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_ERROR_NO_ITEM)
    return [
        Person(uuid=person.uuid, full_name=person.full_name, role=person.role, film_ids=person.film_ids)
        for person in persons
    ]


@router.get('/{person_id}', response_model=Person, summary='Get detailed information about one person.')
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    """
    Return detailed information about one person.

    - **person_id**: uuid of person.
    """
    person = await person_service.get_by_id(person_id, 'Person')
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_ERROR_ITEM_NOT_FOUND)

    return Person(uuid=person.uuid, full_name=person.full_name, role=person.role, film_ids=person.film_ids)


@router.get('/{person_id}/film', summary='Get list of filmworks with specified person')
async def get_person_films(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> List[FilmOut]:
    """
    Return list of filmworks with specified person.

    - **person_id**: uuid of person.
    """
    films = await person_service.get_films_by_id(person_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_ERROR_FILMS_NOT_FOUND)
    return [FilmOut(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]
