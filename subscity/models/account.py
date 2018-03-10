import datetime
import enum
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum
from subscity.models.base import Base, DB


class AccountRole(enum.Enum):
    ADMIN = 1
    API_WRITE = 5
    API_READ = 10


class Account(Base):  # pylint: disable=no-init
    __tablename__ = 'accounts'

    id = Column(Integer, autoincrement=True, primary_key=True)  # pylint: disable=invalid-name
    api_token = Column(String(32), primary_key=True, unique=True)
    name = Column(String(32), nullable=False)
    role = Column(Enum(AccountRole), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        nullable=False)

    def check_role(self, role: 'AccountRole') -> bool:
        return self.role.value <= role.value

    @classmethod
    def check(cls, api_token: Optional[str], role: 'AccountRole') -> bool:
        if not api_token:
            return False
        query = DB.session.query(Account)
        query = query.filter(cls.api_token == api_token)
        query = query.filter(cls.active.is_(True))
        account = query.one_or_none()
        if not account:
            return False
        return account.check_role(role)

    @classmethod
    def add(cls, api_token: str, name: str, role: 'AccountRole') -> 'Account':
        account = Account(api_token=api_token, name=name, role=role, active=True)
        account.save()
        return account
