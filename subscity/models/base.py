import datetime

from sqlalchemy import DateTime

from subscity.main import DB


class Base(DB.Model):
    __abstract__ = True

    @staticmethod
    def format_datetime(date_time):
        if not date_time:
            return None
        return date_time.isoformat()

    def to_dict(self, stringify_datetime=True):  # pylint: disable=R0912
        result = {}
        for c in self.__table__.columns:
            name = c.name
            result[name] = getattr(self, name)

        if stringify_datetime:
            datetime_columns = [c.name for c in self.__table__.columns
                                if isinstance(c.type, DateTime)]
            for column_name in datetime_columns:
                value = getattr(self, column_name)
                if isinstance(value, datetime.datetime):
                    result[column_name] = self.format_datetime(value)
        return result
