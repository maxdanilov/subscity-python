import datetime
from typing import Union

import pytz
from transliterate import translit


def format_datetime(date_time: datetime) -> Union[str, None]:
    if not date_time:
        return None
    return date_time.isoformat()


def get_timezone(city: str) -> str:
    mapping = {}
    return mapping.get(city, 'Europe/Moscow')


def get_now(city: str) -> datetime:
    # returns tz-unaware current time in the timezone of a given city
    utc = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    return utc.astimezone(pytz.timezone(get_timezone(city))).replace(tzinfo=None)


def transliterate(data: str) -> str:
    return translit(data, 'ru', reversed=True) if data else None


def read_file(filename: str) -> str:
    with open(filename, 'r') as file:
        return file.read()
