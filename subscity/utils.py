from datetime import datetime
from typing import Union

from voluptuous import Invalid


def format_datetime(date_time: datetime) -> Union[str, None]:
    if not date_time:
        return None
    return date_time.isoformat()


def validator_date():
    def parse_date(date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
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
