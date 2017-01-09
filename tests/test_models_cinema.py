# -*- coding: utf-8 -*-


class TestModelCinema(object):
    def test_db_empty(self, dbsession):
        from subscity.models.cinema import Cinema
        result = dbsession.query(Cinema).all()
        assert len(result) == 0

    def test_db_add(self, dbsession):
        # from tests.utils import mock_datetime
        # with mock_datetime(datetime.datetime(2017, 1, 2, 3, 4, 5)):
        from subscity.models.cinema import Cinema
        c = Cinema(city_id=1,
                   api_id='deadbeef',
                   name='Cinema')
        dbsession.add(c)
        dbsession.commit()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1

        res = result[0].to_dict()
        res.pop('created_at')
        res.pop('updated_at')
        created_at = result[0].created_at
        updated_at = result[0].updated_at
        assert (updated_at - created_at).total_seconds() < 0.01
        assert res == {'id': 1,
                       'api_id': 'deadbeef',
                       'city_id': 1,
                       'name': 'Cinema',
                       'address': None,
                       'metro': None,
                       'url': None,
                       'phone': None,
                       'fetch_all': False}

        c.name = 'New Näme ъ'
        c.metro = 'metro'
        dbsession.add(c)
        dbsession.commit()
        result2 = dbsession.query(Cinema).all()
        assert len(result2) == 1
        created_at2 = result2[0].created_at
        updated_at2 = result2[0].updated_at
        assert result2[0].name == 'New Näme ъ'
        assert result2[0].metro == 'metro'
        assert created_at2 == created_at
        assert updated_at2 > updated_at
