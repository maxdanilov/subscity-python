import datetime

from sqlalchemy import Boolean
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text
)
from typing import List

from sqlalchemy import Float

from subscity.main import DB
from subscity.models.base import Base


class Movie(Base):  # pylint: disable=no-init
    __tablename__ = 'movies'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    title_en = Column(String(255))

    countries = Column(String(255))
    countries_en = Column(String(255))

    year = Column(Integer)
    age_restriction = Column(Integer)
    duration = Column(Integer)

    languages = Column(String(255))
    languages_en = Column(String(255))

    actors = Column(String(512))
    actors_en = Column(String(512))

    directors = Column(String(255))
    directors_en = Column(String(255))

    genres = Column(String(255))
    genres_en = Column(String(255))

    description = Column(Text())
    description_en = Column(Text())

    premiere = Column(DateTime)

    kinopoisk_id = Column(Integer)
    kinopoisk_rating = Column(Float)
    kinopoisk_votes = Column(Integer)

    imdb_id = Column(Integer)
    imdb_rating = Column(Float)
    imdb_votes = Column(Integer)

    hide = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)
