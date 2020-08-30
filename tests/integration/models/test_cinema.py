# -*- coding: utf-8 -*-


class TestModelCinema(object):
    def test_get_all_empty(self, dbsession):
        from subscity.models.cinema import Cinema
        assert Cinema.get_all() == []

    def test_get_all(self, dbsession):
        from subscity.models.cinema import Cinema
        import datetime
        c1 = Cinema(city='msk', city_id=2, api_id='deadbeef', name='Cinema', url='url',
                    phone='phone', fetch_all=True,
                    created_at=datetime.datetime(2017, 1, 1),
                    updated_at=datetime.datetime(2017, 1, 1))
        c2 = Cinema(city='paris', city_id=4, api_id='badcode', name='Cinema Neu', url=None,
                    phone='phone', fetch_all=False,
                    created_at=datetime.datetime(2017, 1, 1),
                    updated_at=datetime.datetime(2017, 1, 2))
        dbsession.add(c1)
        dbsession.add(c2)
        dbsession.commit()
        result = Cinema.get_all()
        assert len(result) == 2
        assert result[0] == c1
        assert result[1] == c2

    def test_insert_duplicate_api_id(self, dbsession):
        from sqlalchemy.exc import IntegrityError
        import pytest
        from subscity.models.cinema import Cinema
        c1 = Cinema(city='msk', city_id=2, api_id='deadbeef', name='Cinema', url='url',
                    phone='phone', fetch_all=True)
        c2 = Cinema(city='paris', city_id=4, api_id='deadbeef', name='Cinema Neu', url=None,
                    phone='phone', fetch_all=False)
        dbsession.add(c1)
        dbsession.commit()
        dbsession.add(c2)

        with pytest.raises(IntegrityError) as excinfo:
            dbsession.commit()
        assert "Duplicate entry" in str(excinfo.value)

    def test_to_dict(self):
        import datetime
        from subscity.models.cinema import Cinema

        c = Cinema(city='msk',
                   city_id=2,
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   latitude=45.4,
                   longitude=32.1,
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        assert c.to_dict() == {'address': None,
                               'api_id': 'deadbeef',
                               'city': 'msk',
                               'city_id': 2,
                               'created_at': '2017-01-01T00:00:00',
                               'fetch_all': None,
                               'id': None,
                               'metro': None,
                               'name': 'Cinema',
                               'phone': 'phone',
                               'updated_at': '2017-01-01T00:00:00',
                               'latitude': 45.4,
                               'longitude': 32.1,
                               'url': 'url'}

    def test_update_from_dict(self):
        import datetime
        from subscity.models.cinema import Cinema
        c = Cinema(id=12,
                   city='moscow',
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   fetch_all=True,
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        dict_ = {'id': 123, 'city': 'paris', 'url': 'https',
                 'latitude': 21, 'longitude': None, 'fetch_all': None,
                 'created_at': datetime.datetime(2016, 1, 1)}
        c.update_from_dict(dict_, skip_keys=['id', 'url'])
        assert c.id == 12
        assert c.city == 'paris'
        assert c.url == 'url'
        assert c.latitude == 21
        assert c.longitude is None
        assert c.fetch_all is True  # is not nullable
        assert c.created_at == datetime.datetime(2016, 1, 1)

    def test_db_empty(self, dbsession):
        from subscity.models.cinema import Cinema
        result = dbsession.query(Cinema).all()
        assert len(result) == 0

    def test_db_add(self, dbsession):
        from subscity.models.cinema import Cinema
        import datetime
        c = Cinema(city='msk',
                   city_id=2,
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   longitude=12,
                   latitude=16,
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        dbsession.add(c)
        dbsession.commit()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1

        res = result[0].to_dict()
        assert res == {'id': c.id,
                       'api_id': 'deadbeef',
                       'city': 'msk',
                       'city_id': 2,
                       'name': 'Cinema',
                       'address': None,
                       'metro': None,
                       'url': 'url',
                       'phone': 'phone',
                       'fetch_all': False,
                       'longitude': 12,
                       'latitude': 16,
                       'created_at': '2017-01-01T00:00:00',
                       'updated_at': '2017-01-01T00:00:00'}

        c.name = 'New Näme ъ'
        c.metro = 'metro'
        c.fetch_all = True
        dbsession.add(c)
        dbsession.commit()
        result_2 = dbsession.query(Cinema).all()

        assert len(result_2) == 1
        assert result_2[0].name == 'New Näme ъ'
        assert result_2[0].metro == 'metro'
        assert result_2[0].fetch_all is True
        assert result_2[0].created_at == datetime.datetime(2017, 1, 1)
        assert result_2[0].updated_at > datetime.datetime(2017, 1, 1)

    def test_save_or_update_with_same_name(self, dbsession):
        from subscity.models.cinema import Cinema
        import datetime
        c = Cinema(city='msk',
                   city_id=2,
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        c.create_or_update()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1
        assert result[0].to_dict() == c.to_dict()

        d = Cinema(city='paris',
                   city_id=4,
                   api_id='badcode',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   fetch_all=True,
                   created_at=datetime.datetime(2017, 2, 1),
                   updated_at=datetime.datetime(2017, 2, 3))
        d.create_or_update()
        result2 = dbsession.query(Cinema).all()
        assert len(result2) == 2

        assert result2[0].name == 'Cinema'
        assert result2[0].api_id == 'deadbeef'

        assert result2[1].name == 'Cinema'
        assert result2[1].api_id == 'badcode'

    def test_save_or_update_with_same_api_id(self, dbsession):
        from subscity.models.cinema import Cinema
        import datetime
        c = Cinema(city='msk',
                   city_id=2,
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        c.create_or_update()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1
        assert result[0].to_dict() == c.to_dict()

        d = Cinema(city='paris',
                   city_id=4,
                   api_id='deadbeef',
                   name='New Cinema',
                   url='url',
                   phone='phone',
                   fetch_all=True,
                   created_at=datetime.datetime(2017, 2, 1),
                   updated_at=datetime.datetime(2017, 2, 3))
        d.create_or_update()
        result2 = dbsession.query(Cinema).all()
        assert len(result2) == 1
        assert result2[0].to_dict() == {'address': None,
                                        'api_id': 'deadbeef',
                                        'city': 'paris',
                                        'city_id': 4,
                                        'created_at': '2017-02-01T00:00:00',
                                        'fetch_all': True,
                                        'id': c.id,
                                        'metro': None,
                                        'name': 'New Cinema',
                                        'phone': 'phone',
                                        'updated_at': '2017-02-03T00:00:00',
                                        'latitude': None,
                                        'longitude': None,
                                        'url': 'url'}

    def test_save_or_update(self, dbsession):
        from subscity.models.cinema import Cinema
        import datetime
        c = Cinema(city='msk',
                   city_id=2,
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        c.create_or_update()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1
        assert result[0].to_dict() == c.to_dict()

        d = Cinema(city='paris',
                   city_id=4,
                   api_id='badcode',
                   name='New Cinema',
                   url='url',
                   phone='phone',
                   fetch_all=True,
                   created_at=datetime.datetime(2017, 2, 1),
                   updated_at=datetime.datetime(2017, 2, 3))
        d.create_or_update()
        result2 = dbsession.query(Cinema).all()
        assert len(result2) == 2
        assert result2[0].to_dict() == c.to_dict()
        assert result2[1].to_dict() == d.to_dict()

    def test_parse_and_save(self, mocker, dbsession):
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap
        from subscity.models.cinema import Cinema

        with open('tests/fixtures/cinemas/spb/places.xml', 'r') as file:
            fixture_contents = file.read()

        mock_read_file = mocker.patch('subscity.yandex_afisha_parser.read_file')
        mock_read_file.return_value = fixture_contents

        result = Yap.get_cinemas('spb')
        cinema = Cinema(**result[57])
        cinema.create_or_update()

        mock_read_file.assert_called_once_with('/tmp/subscity_afisha_files/afisha_files'
                                               '/spb/cinema/places.xml')

        dbresult = dbsession.query(Cinema).all()
        assert len(dbresult) == 1
        dict_ = dbresult[0].to_dict()
        created_at = dict_.pop('created_at')
        updated_at = dict_.pop('updated_at')
        assert updated_at > created_at
        assert dict_ == {
            'id': cinema.id,
            'api_id': u'580b58f18323013d82c1e980',
            'name': u'Angleterre Cinema Lounge',
            'address': u'ул. Малая Морская, 24, отель «Англетер»',
            'phone': u'+7 (812) 494-59-90, +7 (981) 870-77-57',
            'url': u'http://www.angleterrecinema.ru',
            'metro': u'Адмиралтейская, Садовая, Сенная площадь',
            'city': u'spb',
            'city_id': 3,
            'latitude': 59.933946,
            'longitude': 30.308878,
            'fetch_all': False
        }

    def test_get_by_ids_empty(self, dbsession):
        from subscity.models.cinema import Cinema
        result = Cinema.get_by_ids([1, 2, 3])
        assert result == []

    def test_get_by_ids(self, dbsession):
        from subscity.models.cinema import Cinema
        c1 = Cinema(api_id='fake_cinema1', name='cinema1', city='spb', city_id=3)
        c2 = Cinema(api_id='fake_cinema2', name='cinema2', city='msk', city_id=2)
        c3 = Cinema(api_id='fake_cinema3', name='cinema3', city='msk', city_id=2)
        [dbsession.add(x) for x in [c1, c2, c3]]
        dbsession.commit()
        result = Cinema.get_by_ids([c1.id, c3.id])
        assert result == [c1, c3]

        result2 = Cinema.get_by_ids([])
        assert result2 == []
