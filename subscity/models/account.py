import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from subscity.models.base import Base, DB


class Account(Base):  # pylint: disable=no-init
    __tablename__ = 'accounts'
    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_token = Column(String(32), primary_key=True, unique=True)
    name = Column(String(32), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)

    @classmethod
    def check(cls, api_token: str) -> bool:
        query = DB.session.query(Account)
        query = query.filter(cls.api_token == api_token)
        query = query.filter(cls.active.is_(True))
        return query.one_or_none() is not None

    @classmethod
    def add(cls, api_token: str, name: str) -> 'Account':
        account = Account(api_token=api_token, name=name, active=True)
        account.save()
        return account
