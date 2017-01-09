import datetime
from mock import mock


def mock_datetime(mock_value):
    # taken from: https://solidgeargroup.com/mocking-the-time

    real_datetime_class = datetime.datetime

    class DatetimeSubclassMeta(type):
        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class BaseMockedDatetime(real_datetime_class):
        def __init__(self, *args, **kwargs):
            pass

        @classmethod
        def now(cls, tz=None):
            if tz:
                return tz.localize(mock_value)
            else:
                return mock_value

        @classmethod
        def utcnow(cls):
            return mock_value

        @classmethod
        def today(cls):
            return mock_value

    # Python2 & Python3-compatible metaclass
    mocked_datetime = DatetimeSubclassMeta('datetime', (BaseMockedDatetime,), {})
    return mock.patch.object(datetime, 'datetime', mocked_datetime)
