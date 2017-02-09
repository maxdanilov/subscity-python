import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Numeric,
    or_
)

from subscity.models.base import Base, DB


class Cinema(Base):  # pylint: disable=no-init
    __tablename__ = 'cinemas'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_id = Column(String(64), primary_key=True, unique=True)  # was cinema_id before
    city = Column(String(64), nullable=False)
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

    def create_or_update(self) -> None:
        cls = self.__class__
        query = DB.session.query(cls)
        query = query.filter(or_(cls.name == self.name, cls.api_id == self.api_id))
        obj_in_db = query.one_or_none()
        obj = self

        if obj_in_db:
            update_dict = self.to_dict(stringify_datetime=False)
            obj_in_db.update_from_dict(update_dict)
            obj = obj_in_db

        DB.session.add(obj)
        DB.session.commit()