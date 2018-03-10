import datetime
import enum
from typing import Optional

import bcrypt

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum
from subscity.models.base import Base, DB


class AccountRole(enum.Enum):
    ADMIN = 1
    API_WRITE = 5
    API_READ = 10


class Account(Base):  # pylint: disable=no-init
    __tablename__ = 'accounts'

    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_token = Column(String(256), primary_key=True, unique=True)
    name = Column(String(32), nullable=False)
    role = Column(Enum(AccountRole), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)

    def check_api_token(self, api_token: str) -> bool:
        return bcrypt.checkpw(api_token.encode('utf-8'), self.api_token.encode('utf-8'))

    def check_role(self, role: 'AccountRole') -> bool:
        return self.role.value <= role.value

    @classmethod
    def check(cls, name: Optional[str], api_token: Optional[str], role: 'AccountRole') -> bool:
        if not api_token or not name:
            return False
        query = DB.session.query(Account)
        query = query.filter(cls.name == name)
        query = query.filter(cls.active.is_(True))
        account = query.one_or_none()
        return account is not None \
            and account.check_api_token(api_token) and account.check_role(role)

    def __init__(self, name: Optional[str] = None, api_token: Optional[str] = None,
                 role: Optional['AccountRole'] = None, active: Optional[bool] = True) -> None:
        self.name = name
        self.api_token = bcrypt.hashpw(api_token.encode('utf-8'),
                                       bcrypt.gensalt(Base.BCRYPT_ROUNDS)) if api_token else None
        self.role = role
        self.active = active

    @classmethod
    def add(cls, name: str, api_token: str, role: 'AccountRole') -> 'Account':
        account = Account(name=name, api_token=api_token, role=role, active=True)
        account.save()
        return account
