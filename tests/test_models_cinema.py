# -*- coding: utf-8 -*-


class TestModelCinema(object):
    def test_db_empty(self, dbsession):
        from subscity.models.cinema import Cinema
        result = dbsession.query(Cinema).all()
        assert len(result) == 0

    def test_db_add(self, dbsession):
        from subscity.models.cinema import Cinema
        import datetime
        c = Cinema(city_id=1,
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        dbsession.add(c)
        dbsession.commit()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1

        res = result[0].to_dict()
        assert res == {'id': 1,
                       'api_id': 'deadbeef',
                       'city_id': 1,
                       'name': 'Cinema',
                       'address': None,
                       'metro': None,
                       'url': 'url',
                       'phone': 'phone',
                       'fetch_all': False,
                       'created_at': '2017-01-01T00:00:00',
                       'updated_at': '2017-01-01T00:00:00'}

        c.name = 'New Näme ъ'
        c.metro = 'metro'
        c.fetch_all = True
        dbsession.add(c)
        dbsession.commit()
        result2 = dbsession.query(Cinema).all()

        assert len(result2) == 1
        created_at2 = result2[0].created_at
        updated_at2 = result2[0].updated_at
        assert result2[0].name == 'New Näme ъ'
        assert result2[0].metro == 'metro'
        assert result2[0].fetch_all is True
        assert created_at2 == datetime.datetime(2017, 1, 1)
        assert updated_at2 > datetime.datetime(2017, 1, 1)
