import datetime
from typing import Union, List

from sqlalchemy import DateTime
from sqlalchemy import or_

from subscity.main import DB
from subscity.utils import format_datetime


class Base(DB.Model):  # pylint:disable=no-init
    __abstract__ = True

    def to_dict(self, stringify_datetime: bool=True) -> dict:
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

    def update_from_dict(self, dict_: dict, skip_keys: Union[None]=None):
        skip_keys = skip_keys or ['id']
        for key in dict_.keys():
            if key in self.__table__.columns and key not in skip_keys:
                if not (self.__table__.c[key].nullable is False and not dict_[key]):
                    setattr(self, key, dict_[key])
        return self

    @classmethod
    def get_all(cls) -> List:
        return DB.session.query(cls).all()

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

    def save(self) -> None:
        DB.session.add(self)
        DB.session.commit()

    def delete(self) -> None:
        DB.session.delete(self)
        DB.session.commit()
