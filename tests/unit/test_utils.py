class TestUtils(object):
    def test_format_datetime_none(self):
        from subscity.utils import format_datetime
        result = format_datetime(None)
        assert result is None

    def test_format_datetime(self):
        import datetime
        from subscity.utils import format_datetime
        result = format_datetime(datetime.datetime(2017, 1, 2, 3, 4, 5))
        assert result == '2017-01-02T03:04:05'
