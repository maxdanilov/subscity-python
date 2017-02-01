from subscity.models.movie import Movie
from tests.utils import fread, filter_dict


class TestMovie(object):
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
        assert m.to_dict() == {'api_id': 'deadbeef',
                               'age_restriction': None,
                               'api_id': 'deadbeef',
                               'cast': None,
                               'cast_en': None,
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
        assert filter_dict(result[0].to_dict(), filter_keys) == {
            'api_id': 'bla',
            'title': 'movie',
            'genres': None
        }

        m2 = Movie(api_id='bla2', title='movie2')
        m2.create_or_update()
        result2 = dbsession.query(Movie).all()
        assert len(result2) == 2
        assert result2 == [m, m2]

        assert filter_dict(result2[0].to_dict(), filter_keys) == {
            'api_id': 'bla',
            'title': 'movie',
            'genres': None
        }

        assert filter_dict(result2[1].to_dict(), filter_keys) == {
            'api_id': 'bla2',
            'title': 'movie2',
            'genres': None
        }

        m1 = Movie(api_id='bla')
        m1.create_or_update()
        result3 = dbsession.query(Movie).all()
        assert len(result3) == 2
        assert filter_dict(result3[0].to_dict(), filter_keys) == {
            'api_id': 'bla',
            'title': 'movie',  # is not nullable
            'genres': None
        }

        assert filter_dict(result3[1].to_dict(), filter_keys) == {
            'api_id': 'bla2',
            'title': 'movie2',
            'genres': None
        }

    def test_parse_and_create(self, mocker, dbsession):
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

        fixture = 'fixtures/movies/moscow/5874ea2a685ae0b186614bb5.json'
        mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                     return_value=fread(fixture))
        result = Yap.get_movie('561fdfed37753624b592f13f', 'moscow')
        m = Movie(**result)
        m.save()

        result = dbsession.query(Movie).all()
        assert len(result) == 1

        dict_ = result[0].to_dict()
        created_at = dict_.pop('created_at')
        updated_at = dict_.pop('updated_at')
        assert updated_at > created_at
        assert dict_ == {'api_id': '5874ea2a685ae0b186614bb5',
                         'age_restriction': 16,
                         'cast': 'Райан Гослинг, Эмма Стоун, Финн Уиттрок, Дж.К. Симмонс, '
                                 'Соноя Мидзуно',
                         'cast_en': None,
                         'countries': 'США',
                         'countries_en': None,
                         'description': None,
                         'description_en': None,
                         'directors': 'Дэмьен Шазелл',
                         'directors_en': None,
                         'duration': 128,
                         'genres': 'музыкальный, драма, мелодрама, комедия',
                         'genres_en': 'Musical, Drama, Romance, Comedy',
                         'hide': False,
                         'id': 1,
                         'imdb_id': None,
                         'imdb_rating': None,
                         'imdb_votes': None,
                         'kinopoisk_id': 841081,
                         'kinopoisk_rating': 8.5,
                         'kinopoisk_votes': 42192,
                         'languages': None,
                         'languages_en': None,
                         'premiere': '2017-01-12T00:00:00',
                         'title': 'Ла-Ла Ленд',
                         'title_en': 'La La Land',
                         'year': 2016}
