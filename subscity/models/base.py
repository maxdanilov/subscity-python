import datetime
from typing import Union

from sqlalchemy import DateTime

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
