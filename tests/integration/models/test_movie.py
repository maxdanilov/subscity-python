from subscity.models.movie import Movie


class TestMovie(object):
    @staticmethod
    def _filter_dict(orig, keys):
        return dict(zip(keys, [orig[k] for k in keys]))

    def test_query_empty_result(self, dbsession):
        assert dbsession.query(Movie).all() == []

    def test_get_all_empty(self, dbsession):
        assert Movie.get_all() == []

    def test_get_all(self, dbsession):
        import datetime
        m1 = Movie(id=12, api_id='aaa', title='Title A',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 2))
        m2 = Movie(id=13, api_id='bbb', title='Title B',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 2))
        dbsession.add(m1)
        dbsession.add(m2)
        dbsession.commit()
        result = Movie.get_all()
        assert len(result) == 2
        assert result[0] == m1
        assert result[1] == m2

    def test_to_dict(self):
        import datetime

        m = Movie(api_id='deadbeef',
                  title='Название',
                  title_en='Title',
                  countries='Франция',
                  countries_en='France',
                  created_at=datetime.datetime(2017, 1, 1),
                  updated_at=datetime.datetime(2017, 1, 1))
        assert m.to_dict() == {'actors': None,
                               'actors_en': None,
                               'age_restriction': None,
                               'api_id': 'deadbeef',
                               'countries': 'Франция',
                               'countries_en': 'France',
                               'created_at': '2017-01-01T00:00:00',
                               'description': None,
                               'description_en': None,
                               'directors': None,
                               'directors_en': None,
                               'duration': None,
                               'genres': None,
                               'genres_en': None,
                               'hide': None,
                               'id': None,
                               'imdb_id': None,
                               'imdb_rating': None,
                               'imdb_votes': None,
                               'kinopoisk_id': None,
                               'kinopoisk_rating': None,
                               'kinopoisk_votes': None,
                               'languages': None,
                               'languages_en': None,
                               'premiere': None,
                               'title': 'Название',
                               'title_en': 'Title',
                               'updated_at': '2017-01-01T00:00:00',
                               'year': None}

    def test_create_or_update(self, dbsession):
        filter_keys = ['api_id', 'title', 'genres']
        m = Movie(api_id='bla', title='movie')
        m.create_or_update()
        result = dbsession.query(Movie).all()
        assert len(result) == 1
        assert self._filter_dict(result[0].to_dict(), filter_keys) == {
            'api_id': 'bla',
            'title': 'movie',
            'genres': None
        }

        m2 = Movie(api_id='bla2', title='movie2')
        m2.create_or_update()
        result2 = dbsession.query(Movie).all()
        assert len(result2) == 2
        assert result2 == [m, m2]

        assert self._filter_dict(result2[0].to_dict(), filter_keys) == {
            'api_id': 'bla',
            'title': 'movie',
            'genres': None
        }

        assert self._filter_dict(result2[1].to_dict(), filter_keys) == {
            'api_id': 'bla2',
            'title': 'movie2',
            'genres': None
        }

        m1 = Movie(api_id='bla')
        m1.create_or_update()
        result3 = dbsession.query(Movie).all()
        assert len(result3) == 2
        assert self._filter_dict(result3[0].to_dict(), filter_keys) == {
            'api_id': 'bla',
            'title': 'movie',  # is not nullable
            'genres': None
        }

        assert self._filter_dict(result3[1].to_dict(), filter_keys) == {
            'api_id': 'bla2',
            'title': 'movie2',
            'genres': None
        }
