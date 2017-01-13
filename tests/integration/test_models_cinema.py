# -*- coding: utf-8 -*-


class TestModelCinema(object):

    def test_to_dict(self):
        import datetime
        from subscity.models.cinema import Cinema
        c = Cinema(city='moscow',
                   api_id='deadbeef',
                   name='Cinema',
                   url='url',
                   phone='phone',
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
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 1))
        dict_ = {'id': 123, 'city': 'paris', 'url': 'https',
                 'created_at': datetime.datetime(2016, 1, 1)}
        c.update_from_dict(dict_, skip_keys=['id', 'url'])
        assert c.id == 12
        assert c.city == 'paris'
        assert c.url == 'url'
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
