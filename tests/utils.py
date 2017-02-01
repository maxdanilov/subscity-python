import datetime
import os

from mock import mock


def fread(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def filter_dict(orig, keys):
    return dict(zip(keys, [orig[k] for k in keys]))


def mock_datetime(mock_value):
    # taken from: https://solidgeargroup.com/mocking-the-time

    real_datetime_class = datetime.datetime

    class DatetimeSubclassMeta(type):
        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class BaseMockedDatetime(real_datetime_class):
        @classmethod
        def now(cls):
            return mock_value

    # Python2 & Python3-compatible metaclass
    mocked_datetime = DatetimeSubclassMeta('datetime', (BaseMockedDatetime,), {})
    return mock.patch.object(datetime, 'datetime', mocked_datetime)
