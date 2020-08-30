import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    Text, SmallInteger
)

from subscity.models.base import Base, DB


class Movie(Base):  # pylint: disable=no-init
    __tablename__ = 'movies-v2'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_id = Column(String(64), primary_key=True, unique=True)

    active = Column(Boolean)

    title = Column(String(255), nullable=False)
    title_original = Column(String(255))

    languages = Column(String(255))

    description = Column(Text())
    description_english = Column(Text())

    director = Column(String(255))
    cast = Column(String(512))

    age_restriction = Column(Integer)

    country = Column(String(255))

    year = Column(Integer)
    genres = Column(String(255))

    poster = Column(String(512))

    duration = Column(Integer)

    kinopoisk_id = Column(Integer)
    imdb_id = Column(Integer)

    trailer = Column(String(255))

    fetch_mode = Column(SmallInteger, default=0, nullable=False)  # legacy: for v1 compatibility

    premiere = Column(DateTime)

    hide = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)

    @classmethod
    def get_hidden_api_ids(cls) -> List[str]:
        query = DB.session.query(cls.api_id)
        query = query.filter(cls.hide.is_(True))
        return [x[0] for x in query.all()]
