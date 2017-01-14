import datetime
from typing import List

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)
from sqlalchemy import Float

from subscity.main import DB
from subscity.models.base import Base
from subscity.yandex_afisha_parser import YandexAfishaParser


class Screening(Base):  # pylint: disable=no-init
    __tablename__ = 'screenings'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    cinema_api_id = Column(String(64), primary_key=True)
    movie_api_id = Column(String(64), primary_key=True)
    ticket_api_id = Column(String(128), nullable=True)
    city = Column(String(64), nullable=False)
    date_time = Column(DateTime, default=None, nullable=False)
    price_min = Column(Float, nullable=True)
    price_max = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)

    # TODO: cleanup old

    @staticmethod
    def get(cinema_api_id: str=None, movie_api_id: str=None, day: datetime=None,
            city: str=None) -> List:
        query = DB.session.query(Screening)
        query = query.filter(Screening.cinema_api_id == cinema_api_id if cinema_api_id else True)
        query = query.filter(Screening.movie_api_id == movie_api_id if movie_api_id else True)
        query = query.filter(Screening.city == city if city else True)
        if day:
            date = day.replace(hour=0, minute=0, second=0, microsecond=0)
            date_start = date + YandexAfishaParser.DAY_STARTS_AT
            date_end = date_start + datetime.timedelta(days=1)
            query = query.filter(Screening.date_time >= date_start, Screening.date_time <= date_end)
        query = query.order_by(Screening.date_time)
        return query.all()

    def save(self) -> None:
        DB.session.add(self)
        DB.session.commit()
