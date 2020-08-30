import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    Text
)

from subscity.models.base import Base, DB


class Movie(Base):  # pylint: disable=no-init
    __tablename__ = 'movies'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_id = Column(String(64), primary_key=True, unique=True)

    active = Column(Boolean)

    title = Column(String(255), nullable=False)
    title_original = Column(String(255))

    languages = Column(String(255))

    description = Column(Text())
    description_english = Column(Text())

    director = Column(String(255))

    countries = Column(String(255))
    countries_en = Column(String(255))

    year = Column(Integer)
    age_restriction = Column(Integer)
    duration = Column(Integer)

    cast = Column(String(512))
    cast_en = Column(String(512))

    genres = Column(String(255))
    genres_en = Column(String(255))

    poster_url = Column(String(512))
    premiere = Column(DateTime)

    kinopoisk_id = Column(Integer)

    imdb_id = Column(Integer)

    hide = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)

    @classmethod
    def get_hidden_api_ids(cls) -> List[str]:
        query = DB.session.query(cls.api_id)
        query = query.filter(cls.hide.is_(True))
        return [x[0] for x in query.all()]
