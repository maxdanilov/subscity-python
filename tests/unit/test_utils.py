import pytest
import datetime

parametrize = pytest.mark.parametrize


class TestUtils(object):
    def test_format_datetime_none(self):
        from subscity.utils import format_datetime
        result = format_datetime(None)
        assert result is None

    def test_format_datetime(self):
        from subscity.utils import format_datetime
        result = format_datetime(datetime.datetime(2017, 1, 2, 3, 4, 5))
        assert result == '2017-01-02T03:04:05'

    def test_mock_datetime(self):
        from tests.utils import mock_datetime
        with mock_datetime(datetime.datetime(2017, 1, 1)):
            assert datetime.datetime.now() == datetime.datetime(2017, 1, 1)
            assert isinstance(datetime.datetime.now(), datetime.datetime)

    @parametrize('data, expected', [('2015-01-31', datetime.datetime(2015, 1, 31)),
                                    ('2016-02-29', datetime.datetime(2016, 2, 29))])
    def test_validator_date_valid(self, data, expected):
        from subscity.utils import validator_date
        result = validator_date()(data)
        assert result == expected

    @parametrize('data', ['2015-01-31T12:00:00', '2015-02-29', 'wrong', None])
    def test_validator_date_invalid(self, data):
        from voluptuous import Invalid
        from subscity.utils import validator_date

        with pytest.raises(Invalid) as excinfo:
            validator_date()(data)
        assert 'date should be in this format: YYYY-MM-DD' in str(excinfo.value)

    @parametrize('data, expected', [('msk', 'moscow'), ('spb', 'saint-petersburg')])
    def test_validator_city_valid(self, data, expected):
        from subscity.utils import validator_city
        result = validator_city()(data)
        assert result == expected

    @parametrize('data', ['Msk', 'SPB', None])
    def test_validator_city_invalid(self, data):
        from voluptuous import Invalid
        from subscity.utils import validator_city

        with pytest.raises(Invalid) as excinfo:
            validator_city()(data)
        assert 'city should be one of: msk, spb' in str(excinfo.value)

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

    def test_download_to_json(self, mocker):
        from tests.utils import download_to_json
        from mock import mock_open, patch, call
        from subscity.yandex_afisha_parser import YandexAfishaParser

        mock_file_open = mock_open()
        mock_fetch = mocker.patch.object(YandexAfishaParser, 'fetch', return_value='{"json": 1}')

        with patch('tests.utils.open', mock_file_open, create=True):
            download_to_json('url', 'filename')

        mock_fetch.assert_called_once_with('url')
        mock_file_open.assert_called_once_with('filename', 'w')
        assert mock_file_open.mock_calls[2] == call().write('{\n    "json": 1\n}')

    @parametrize('data, expected', [(None, None),
                                    ("", None),
                                    ("<p>some &amp; <b>mar&lt;k&gt;up</b></p>", "some & mar<k>up"),
                                    ("<p>new<br/>line</p>", "new\nline"),
                                    ("<p>par1</p><p>par2</p>", "par1\npar2")])
    def test_html_to_text(self, data, expected):
        from subscity.utils import html_to_text
        assert html_to_text(data) == expected
