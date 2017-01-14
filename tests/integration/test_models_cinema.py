# -*- coding: utf-8 -*-
import os


class TestModelCinema(object):
    def _fread(self, fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    def test_to_dict(self):
        import datetime
        from subscity.models.cinema import Cinema

        c = Cinema(city='moscow',
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
                               'city': 'moscow',
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
        c = Cinema(city='moscow',
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
                       'city': 'moscow',
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
        c = Cinema(city='moscow',
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        c.save_or_update()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1
        assert result[0].to_dict() == c.to_dict()

        d = Cinema(city='paris',
                   api_id='badcode',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   fetch_all=True,
                   created_at=datetime.datetime(2017, 2, 1),
                   updated_at=datetime.datetime(2017, 2, 3))
        d.save_or_update()
        result2 = dbsession.query(Cinema).all()
        assert len(result2) == 1
        assert result2[0].to_dict() == {'address': None,
                                        'api_id': 'badcode',
                                        'city': 'paris',
                                        'created_at': '2017-02-01T00:00:00',
                                        'fetch_all': True,
                                        'id': c.id,
                                        'metro': None,
                                        'name': 'Cinema',
                                        'phone': 'phone',
                                        'updated_at': '2017-02-03T00:00:00',
                                        'latitude': None,
                                        'longitude': None,
                                        'url': 'url'}

    def test_save_or_update_with_same_api_id(self, dbsession):
        from subscity.models.cinema import Cinema
        import datetime
        c = Cinema(city='moscow',
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        c.save_or_update()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1
        assert result[0].to_dict() == c.to_dict()

        d = Cinema(city='paris',
                   api_id='deadbeef',
                   name='New Cinema',
                   url='url',
                   phone='phone',
                   fetch_all=True,
                   created_at=datetime.datetime(2017, 2, 1),
                   updated_at=datetime.datetime(2017, 2, 3))
        d.save_or_update()
        result2 = dbsession.query(Cinema).all()
        assert len(result2) == 1
        assert result2[0].to_dict() == {'address': None,
                                        'api_id': 'deadbeef',
                                        'city': 'paris',
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
        c = Cinema(city='moscow',
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        c.save_or_update()
        result = dbsession.query(Cinema).all()
        assert len(result) == 1
        assert result[0].to_dict() == c.to_dict()

        d = Cinema(city='paris',
                   api_id='badcode',
                   name='New Cinema',
                   url='url',
                   phone='phone',
                   fetch_all=True,
                   created_at=datetime.datetime(2017, 2, 1),
                   updated_at=datetime.datetime(2017, 2, 3))
        d.save_or_update()
        result2 = dbsession.query(Cinema).all()
        assert len(result2) == 2
        assert result2[0].to_dict() == c.to_dict()
        assert result2[1].to_dict() == d.to_dict()

    def test_parse_and_save(self, mocker, dbsession):
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap
        from subscity.models.cinema import Cinema

        fixtures_path = '../fixtures/cinemas/saint-petersburg/'
        mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                     side_effect=[
                         self._fread(fixtures_path + 'cinemas-offset00-limit20.json'),
                         self._fread(fixtures_path + 'cinemas-offset20-limit20.json'),
                         self._fread(fixtures_path + 'cinemas-offset40-limit20.json'),
                         self._fread(fixtures_path + 'cinemas-offset60-limit20.json')])
        result = Yap.get_cinemas('saint-petersburg')
        cinema = Cinema(**result[37])
        cinema.save_or_update()

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
            'city': u'saint-petersburg',
            'latitude': 59.933946,
            'longitude': 30.308878,
            'fetch_all': False
        }
