import pytest
import datetime

parametrize = pytest.mark.parametrize


class TestUtils(object):
    def test_read_file(self):
        from subscity.utils import read_file
        result = read_file('pytest.ini')
        assert result == '[pytest]\n\naddopts=--cov=subscity subscity/ --cov=tests ' \
                         '--cov-report html -v\n'

    def test_mock_datetime(self):
        from tests.utils import mock_datetime
        with mock_datetime(datetime.datetime(2017, 1, 1)):
            assert datetime.datetime.now() == datetime.datetime(2017, 1, 1)
            assert isinstance(datetime.datetime.now(), datetime.datetime)

    @parametrize('city, expected', [('moscow', 'Europe/Moscow'),
                                    ('saint-petersburg', 'Europe/Moscow')])
    def test_get_timezone(self, city, expected):
        from subscity.utils import get_timezone
        assert get_timezone(city) == expected

    @parametrize('utc_now, expected', [(datetime.datetime(2017, 2, 15, 10, 0),   # winter time
                                        datetime.datetime(2017, 2, 15, 13, 0)),
                                       (datetime.datetime(2017, 6, 15, 10, 0),   # summer time
                                        datetime.datetime(2017, 6, 15, 13, 0))])
    def test_get_now(self, utc_now, expected):
        from subscity.utils import get_now
        from tests.utils import mock_datetime
        with mock_datetime(mock_utcnow=utc_now):
            assert get_now('moscow') == expected

    @parametrize('data, expected', [(None, None),
                                    ('5 Звезд на Новокузнецкой', '5 Zvezd na Novokuznetskoj'),
                                    ('Синема Lounge', 'Sinema Lounge')])
    def test_transliterate(self, data, expected):
        from subscity.utils import transliterate
        assert transliterate(data) == expected
