import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean
)

from subscity.models.base import Base


class Cinema(Base):  # pylint: disable=no-init
    __tablename__ = 'cinemas'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_id = Column(String(64), primary_key=True)  # was cinema_id before
    city = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    metro = Column(String(255), nullable=True)
    url = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    fetch_all = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)

    @staticmethod
    def get(data):
        # either fetch one from DB with api_id
        # or create one if if doesn't exist
        pass

    def save(self):
        pass
