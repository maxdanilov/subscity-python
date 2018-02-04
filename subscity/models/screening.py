import datetime
from typing import List

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)
from sqlalchemy import Float
from sqlalchemy import func
from sqlalchemy.dialects.mysql import DATETIME

from subscity.models.base import Base, DB
from subscity.models.cinema import Cinema
from subscity.models.movie import Movie
from subscity.utils import get_now
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap


class Screening(Base):  # pylint: disable=no-init
    __tablename__ = 'screenings'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    cinema_api_id = Column(String(64), primary_key=True)
    movie_api_id = Column(String(64), primary_key=True)
    ticket_api_id = Column(String(128), nullable=True)
    city = Column(String(64), nullable=False)
    date_time = Column(DateTime, nullable=False, primary_key=True)
    price_min = Column(Float, nullable=True)
    source = Column(String(32), nullable=False)

    created_at = Column(DATETIME(fsp=6), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DATETIME(fsp=6), default=datetime.datetime.now,
                        onupdate=datetime.datetime.now, nullable=False)

    @property
    def day(self):
        start_day = self.date_time.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.date_time > start_day + Yap.DAY_STARTS_AT:
            return start_day
        return start_day - datetime.timedelta(days=1)

    @staticmethod
    def get_for_movie(movie_id: int, city: str) -> List:
        movie_api_id = DB.session.query(Movie.api_id).filter(Movie.id == movie_id).as_scalar()
        query = DB.session.query(Screening, Movie, Cinema)
        query = query.filter(Screening.city == city)
        query = query.filter(Screening.movie_api_id == movie_api_id)
        query = query.filter(Screening.cinema_api_id == Cinema.api_id)
        query = query.filter(Screening.movie_api_id == Movie.api_id)
        query = query.filter(Screening.date_time > get_now(city))
        query = query.order_by(Screening.date_time)
        return query.all()

    @staticmethod
    def get_for_cinema(cinema_id: int, city: str) -> List:
        cinema_api_id = DB.session.query(Cinema.api_id).filter(Cinema.id == cinema_id).as_scalar()
        query = DB.session.query(Screening, Movie, Cinema)
        query = query.filter(Screening.city == city)
        query = query.filter(Screening.cinema_api_id == cinema_api_id)
        query = query.filter(Screening.cinema_api_id == Cinema.api_id)
        query = query.filter(Screening.movie_api_id == Movie.api_id)
        query = query.filter(Screening.date_time > get_now(city))
        query = query.filter(Movie.hide.is_(False))
        query = query.order_by(Screening.date_time)
        return query.all()

    @staticmethod
    def get_for_day(day: datetime, city: str) -> List:
        start_day = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end_day = start_day + datetime.timedelta(days=1)
        query = DB.session.query(Screening, Movie, Cinema)
        query = query.filter(Screening.date_time > start_day + Yap.DAY_STARTS_AT)
        query = query.filter(Screening.date_time <= end_day + Yap.DAY_STARTS_AT)
        query = query.filter(Screening.city == city)
        query = query.filter(Screening.cinema_api_id == Cinema.api_id)
        query = query.filter(Screening.movie_api_id == Movie.api_id)
        query = query.filter(Screening.date_time > get_now(city))
        query = query.order_by(Screening.date_time)
        return query.all()

    @staticmethod
    def get(cinema_api_id: str = None, movie_api_id: str = None, start_day: datetime = None,
            end_day: datetime = None, city: str = None) -> List:
        query = DB.session.query(Screening)
        query = query.filter(Screening.cinema_api_id == cinema_api_id if cinema_api_id else True)
        query = query.filter(Screening.movie_api_id == movie_api_id if movie_api_id else True)
        query = query.filter(Screening.city == city if city else True)
        if start_day:
            start_day = start_day.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Screening.date_time > start_day + Yap.DAY_STARTS_AT)
        if end_day:
            end_day = end_day.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Screening.date_time <= end_day + Yap.DAY_STARTS_AT)
        query = query.order_by(Screening.date_time)
        return query.all()

    @staticmethod
    def get_movies_cinemas(city: str) -> List:
        query = DB.session.query(Cinema.id.label('cinema_id'),
                                 Movie.id.label('movie_id'))
        query = query.filter(Screening.date_time > get_now(city))
        query = query.filter(Screening.cinema_api_id == Cinema.api_id)
        query = query.filter(Screening.movie_api_id == Movie.api_id)
        query = query.filter(Movie.hide.is_(False))
        query = query.filter(Screening.city == city)
        query = query.distinct()
        return query.all()

    @staticmethod
    def get_movie_api_ids(city: str) -> List:
        # NB: hidden movies are not filtered here
        query = DB.session.query(func.min(Screening.date_time).label('next_screening'),
                                 func.count().label('screenings'),
                                 Screening.movie_api_id)
        query = query.filter(Screening.city == city)
        query = query.filter(Screening.date_time > get_now(city))
        query = query.group_by(Screening.movie_api_id)
        return query.all()

    @staticmethod
    def clean(cinema_api_id: str = None, movie_api_id: str = None, start_day: datetime = None,
              end_day: datetime = None, city: str = None) -> int:
        screenings = Screening.get(cinema_api_id, movie_api_id, start_day, end_day, city)
        for screening in screenings:
            screening.delete()
        return len(screenings)
