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
