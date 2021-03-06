import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Numeric
)

from subscity.models.base import Base, DB
from subscity.utils import transliterate


class Cinema(Base):  # pylint: disable=no-init
    __tablename__ = 'cinemas-v2'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_id = Column(String(64), primary_key=True, unique=True)  # was cinema_id before
    city = Column(String(64), nullable=False)
    city_id = Column(Integer, nullable=False)  # legacy, kept for compatibility with v1
    name = Column(String(255), primary_key=True)
    address = Column(String(512), nullable=True)
    metro = Column(String(255), nullable=True)
    url = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    fetch_all = Column(Boolean, default=False, nullable=False)
    latitude = Column(Numeric(precision=11, scale=8), nullable=True)
    longitude = Column(Numeric(precision=11, scale=8), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)

    @property
    def address_en(self) -> str:
        return transliterate(self.address)

    @property
    def name_en(self) -> str:
        return transliterate(self.name)

    @property
    def metro_en(self) -> str:
        return transliterate(self.metro)

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
