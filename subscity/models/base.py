import datetime
from typing import Union, List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime

from subscity.app import get_app
from subscity.utils import format_datetime

APP = get_app()
DB = SQLAlchemy(APP)


class Base(DB.Model):  # pylint:disable=no-init
    __abstract__ = True

    BCRYPT_ROUNDS = 12

    def to_dict(self, stringify_datetime: bool = True) -> dict:
        result = {}
        for column in self.__table__.columns:
            name = column.name
            result[name] = getattr(self, name)

        if stringify_datetime:
            datetime_columns = [c.name for c in self.__table__.columns
                                if isinstance(c.type, DateTime)]
            for column_name in datetime_columns:
                value = getattr(self, column_name)
                if isinstance(value, datetime.datetime):
                    result[column_name] = format_datetime(value)
        return result

    def update_from_dict(self, dict_: dict, skip_keys: Union[None] = None):
        skip_keys = skip_keys or ['id']
        for key in dict_.keys():
            if key in self.__table__.columns and key not in skip_keys:
                if not (self.__table__.c[key].nullable is False and not dict_[key]):
                    setattr(self, key, dict_[key])
        return self

    @classmethod
    def get_all(cls) -> List:
        return DB.session.query(cls).all()

    @classmethod
    def get_all_api_ids(cls) -> List:
        rows = DB.session.query(cls.api_id).all()  # pylint:disable=no-member
        return [r.api_id for r in rows]

    @classmethod
    def get_by_id(cls, id_: int):
        query = DB.session.query(cls)
        query = query.filter(cls.id == id_)
        return query.one_or_none()

    @classmethod
    def get_by_ids(cls, ids: List[int]) -> List:
        query = DB.session.query(cls)
        query = query.filter(cls.id.in_(ids))  # pylint:disable=no-member
        return query.all()

    @classmethod
    def get_by_api_ids(cls, api_ids) -> List:
        query = DB.session.query(cls)
        query = query.filter(cls.api_id.in_(api_ids))  # pylint:disable=no-member
        return query.all()

    def save(self) -> None:
        DB.session.add(self)
        DB.session.commit()

    def delete(self) -> None:
        DB.session.delete(self)
        DB.session.commit()
