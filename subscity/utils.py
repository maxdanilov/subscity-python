from datetime import datetime
from typing import Union


def format_datetime(date_time: datetime) -> Union[str, None]:
    if not date_time:
        return None
    return date_time.isoformat()
