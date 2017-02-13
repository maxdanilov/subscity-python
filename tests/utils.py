import datetime
import json
import os

from mock import mock
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap


def fread(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def filter_dict(orig, keys):
    return dict(zip(keys, [orig[k] for k in keys]))


def download_to_json(url, filename):
    print("Downloading {} to {}".format(url, filename))
    parsed = json.loads(Yap.fetch(url))
    with open(filename, "w") as file:
        file.write(json.dumps(parsed, indent=4))


def mock_datetime(mock_now=None, mock_utcnow=None):
    # taken from: https://solidgeargroup.com/mocking-the-time

    real_datetime_class = datetime.datetime

    class DatetimeSubclassMeta(type):
        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class BaseMockedDatetime(real_datetime_class):
        @classmethod
        def now(cls):
            return mock_now

        @classmethod
        def utcnow(cls):
            return mock_utcnow

    # Python2 & Python3-compatible metaclass
    mocked_datetime = DatetimeSubclassMeta('datetime', (BaseMockedDatetime,), {})
    return mock.patch.object(datetime, 'datetime', mocked_datetime)
