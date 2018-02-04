import datetime
import json
from typing import Union

from bs4 import BeautifulSoup
from flask import Response
import pytz
from transliterate import translit
from voluptuous import Invalid, MultipleInvalid


def json_response(data):
    # unlike Flask's jsonify this one doesn't escape unicode characters
    return Response(json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True).
                    encode('utf8'), mimetype='application/json')


def format_datetime(date_time: datetime) -> Union[str, None]:
    if not date_time:
        return None
    return date_time.isoformat()


def validator_date():
    def parse_date(date_str: str) -> datetime:
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            raise Invalid('date should be in this format: YYYY-MM-DD')
    return parse_date


def validator_city():
    def city_by_code(code: str) -> str:
        mapping = {'msk': 'moscow', 'spb': 'saint-petersburg'}
        if code not in mapping:
            raise Invalid('city should be one of: msk, spb')
        return mapping[code]
    return city_by_code


def error_msg(exc: MultipleInvalid) -> dict:
    return {'errors': [e.msg for e in exc.errors]}


def get_timezone(city: str) -> str:
    mapping = {}
    return mapping.get(city, 'Europe/Moscow')


def get_now(city: str) -> datetime:
    # returns tz-unaware current time in the timezone of a given city
    utc = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    return utc.astimezone(pytz.timezone(get_timezone(city))).replace(tzinfo=None)


def transliterate(data: str) -> str:
    return translit(data, 'ru', reversed=True) if data else None


def html_to_text(data: str) -> str:
    if data:
        soup = BeautifulSoup(data, "html.parser")
        text = soup.get_text(separator='\n')
        text = text.replace('& \n', '& ')  # for some reason, BS adds a line break after &amp;
        return text


def read_file(filename: str) -> str:
    with open(filename, 'r') as file:
        return file.read()
