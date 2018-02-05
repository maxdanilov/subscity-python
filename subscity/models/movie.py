import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    Float,
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
    title = Column(String(255), nullable=False)
    title_en = Column(String(255))

    countries = Column(String(255))
    countries_en = Column(String(255))

    year = Column(Integer)
    age_restriction = Column(Integer)
    duration = Column(Integer)

    languages = Column(String(255))
    languages_en = Column(String(255))

    cast = Column(String(512))
    cast_en = Column(String(512))

    directors = Column(String(255))
    directors_en = Column(String(255))

    genres = Column(String(255))
    genres_en = Column(String(255))

    description = Column(Text())
    description_en = Column(Text())

    poster_url = Column(String(512))
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

    # TODO test me
    @classmethod
    def get_hidden_api_ids(cls) -> List[str]:
        query = DB.session.query(cls.api_id)
        query = query.filter(cls.hide.is_(True))
        return [x[0] for x in query.all()]

    def create_or_update(self) -> None:
        cls = self.__class__
        query = DB.session.query(cls)
        query = query.filter(cls.api_id == self.api_id)
        obj_in_db = query.one_or_none()
        obj = self

        if obj_in_db:
            update_dict = self.to_dict(stringify_datetime=False)
            obj_in_db.update_from_dict(update_dict)
            obj = obj_in_db

        DB.session.add(obj)
        DB.session.commit()
