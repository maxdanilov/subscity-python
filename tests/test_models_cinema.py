import datetime


class TestModelCinema(object):
    def test_db_empty(self, dbsession):
        from subscity.models.cinema import Cinema
        result = dbsession.query(Cinema).all()
        assert len(result) == 0

    def test_db_add(self, dbsession):
        from tests.utils import mock_datetime
        with mock_datetime(datetime.datetime(2017, 1, 2, 3, 4, 5)):
            from subscity.models.cinema import Cinema
            c = Cinema(city_id=1,
                       api_id='deadbeef',
                       name='Cinema')
            dbsession.add(c)
            dbsession.commit()
            result = dbsession.query(Cinema).all()
            assert len(result) == 1

            res = result[0].to_dict()
            created_at = res.pop('created_at')
            updated_at = res.pop('updated_at')
            # assert created_at == updated_at
            assert res == {'id': 1,
                           'api_id': 'deadbeef',
                           'city_id': 1,
                           'name': 'Cinema',
                           'address': None,
                           'metro': None,
                           'url': None,
                           'phone': None,
                           'fetch_all': False}
