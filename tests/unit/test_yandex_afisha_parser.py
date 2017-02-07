# -*- coding: utf-8 -*-

import os

import pytest
from mock import call
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

parametrize = pytest.mark.parametrize


class TestYandexAfishaParser(object):
    def _fread(self, fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    @parametrize('limit, offset, city, expected',
                 [(20, 40, 'moscow',
                   'https://afisha.yandex.ru/api/events/cinema/places?limit=20&offset=40&'
                   'city=moscow'),
                  (11, '42', 'saint-petersburg',
                   'https://afisha.yandex.ru/api/events/cinema/places?limit=11&offset=42&'
                   'city=saint-petersburg')])
    def test_url_cinemas(self, limit, offset, city, expected):
        assert Yap.url_cinemas(limit, offset, city) == expected

    @parametrize('limit, offset, city, expected',
                 [(20, 40, 'moscow',
                   'https://afisha.yandex.ru/api/events/actual?limit=20&offset=40&'
                   'tag=cinema&hasMixed=0&city=moscow'),
                  (11, '42', 'saint-petersburg',
                   'https://afisha.yandex.ru/api/events/actual?limit=11&offset=42&'
                   'tag=cinema&hasMixed=0&city=saint-petersburg')])
    def test_url_movies(self, limit, offset, city, expected):
        assert Yap.url_movies(limit, offset, city) == expected

    def test_url_movie(self):
        result = Yap.url_movie('mock_id', 'mock_city')
        assert result == 'https://afisha.yandex.ru/api/events/mock_id?city=mock_city'

    def test_url_movie_default_city(self):
        result = Yap.url_movie('mock_id')
        assert result == 'https://afisha.yandex.ru/api/events/mock_id?city=moscow'

    def test_url_cinema_schedule(self):
        from datetime import datetime
        result = Yap.url_cinema_schedule(api_id='fake_id', date=datetime(2016, 1, 12),
                                         city='fake_city')
        expected = "https://afisha.yandex.ru/api/places/fake_id/schedule_cinema?date=2016-01-12&" \
                   "city=fake_city"
        assert result == expected

    def test_fetch(self, mocker):
        class UrlOpenResultFake(object):
            def read(self):
                return 'fake-val'

        mock_url_open = mocker.patch('urllib.request.urlopen', return_value=UrlOpenResultFake())
        assert Yap.fetch('some-url') == 'fake-val'
        mock_url_open.assert_called_once_with('some-url')

    def test_get_countries(self):
        assert Yap._get_countries(None) is None
        assert Yap._get_countries([]) is None
        assert Yap._get_countries(['США', 'Франция']) == 'США, Франция'

    def test_get_age_restriction(self):
        assert Yap._get_age_restriction(None) is None
        assert Yap._get_age_restriction('') is None
        assert Yap._get_age_restriction('0+') == 0
        assert Yap._get_age_restriction('6+') == 6
        assert Yap._get_age_restriction('12+') == 12
        assert Yap._get_age_restriction('16+') == 16
        assert Yap._get_age_restriction('18+') == 18
        assert Yap._get_age_restriction('17') == 17

    def test_get_premiere(self):
        from datetime import datetime
        assert Yap._get_premiere(None) is None
        assert Yap._get_premiere('') is None
        assert Yap._get_premiere('2017-01-12') == datetime(2017, 1, 12)

    def test_get_actors(self):
        assert Yap._get_actors(None) is None
        assert Yap._get_actors('') is None
        assert Yap._get_actors([]) is None
        assert Yap._get_actors([{'role': 'actor', 'names': []}]) is None
        assert Yap._get_actors([{'role': 'actor', 'names': ['Чарли Чаплин']}]) == 'Чарли Чаплин'
        data = [{'role': 'actor',
                 'names': ['Райан Гослинг', 'Эмма Стоун', 'Финн Уиттрок', 'Дж.К. Симмонс']},
                {'role': 'director', 'names': ['Дэмьен Шазелл']}]
        assert Yap._get_actors(data) == 'Райан Гослинг, Эмма Стоун, Финн Уиттрок, Дж.К. Симмонс'

    def test_get_directors(self):
        assert Yap._get_directors(None) is None
        assert Yap._get_directors('') is None
        assert Yap._get_directors([]) is None
        assert Yap._get_directors([{'role': 'director', 'names': []}]) is None
        assert Yap._get_directors([{'role': 'director', 'names': ['Стэнли Кубрик']}]) == \
            'Стэнли Кубрик'
        data = [{'role': 'actor',
                 'names': ['Райан Гослинг', 'Эмма Стоун', 'Финн Уиттрок', 'Дж.К. Симмонс']},
                {'role': 'director', 'names': ['Дэмьен Шазелл', 'Стэнли Кубрик']}]
        assert Yap._get_directors(data) == 'Дэмьен Шазелл, Стэнли Кубрик'

    def test_get_kinopoisk_data(self):
        empty = {'id': None, 'rating': None, 'votes': None}
        assert Yap._get_kinopoisk_data(None) == empty
        assert Yap._get_kinopoisk_data({}) == empty

        data = {'url': 'http://kinopoisk.ru/film/841081', 'value': 8.5, 'votes': 42192}
        assert Yap._get_kinopoisk_data(data) == {'id': 841081,
                                                 'rating': 8.5,
                                                 'votes': 42192}

    def test_get_original_genre(self):
        assert Yap._get_original_genre('') == ''
        assert Yap._get_original_genre('drama') == 'Drama'
        assert Yap._get_original_genre('musical_film') == 'Musical'
        assert Yap._get_original_genre('art_film') == 'Indie Film'

    def test_get_genres(self):
        empty = {'russian': None, 'original': None}
        assert Yap._get_genres(None) == empty
        assert Yap._get_genres([]) == empty
        data = [{'id': '57272d9c10048dda13c470ba', 'code': 'musical_film', 'type': 'genre',
                 'status': 'approved', 'name': 'музыкальный', 'plural': None,
                 'nameCases': {'acc': None, 'gen': None}},
                {'id': '57d2843efc8131fcefa33f9f', 'code': 'drama', 'type': 'genre',
                 'status': 'approved', 'name': 'драма', 'plural': None,
                 'nameCases': {'acc': None, 'gen': None}},
                {'id': '5575d413cc1c724f5a8e10f6', 'code': 'romance', 'type': 'genre',
                 'status': 'approved', 'name': 'мелодрама', 'plural': None,
                 'nameCases': {'acc': None, 'gen': None}},
                {'id': '57d28482377536932cfc4c2e', 'code': 'comedy', 'type': 'genre',
                 'status': 'approved', 'name': 'комедия', 'plural': None,
                 'nameCases': {'acc': None, 'gen': None}},
                {'id': '5591526f37753645b7d7a5ed', 'code': 'cinema', 'type': 'format',
                 'status': 'approved', 'name': 'кино', 'plural': {'one': 'кино', 'some': 'фильма',
                                                                  'many': 'фильмов', 'none': None},
                 'nameCases': {'acc': 'в кинотеатрах', 'gen': None}}]
        assert Yap._get_genres(data) == {'original': 'Musical, Drama, Romance, Comedy',
                                         'russian': 'музыкальный, драма, мелодрама, комедия'}

    @parametrize('city', ['moscow', 'saint-petersburg'])
    def test_get_movie(self, city, mocker):
        from datetime import datetime
        api_id = '5874ea2a685ae0b186614bb5'
        fixture = '../fixtures/movies/{}/{}.json'.format(city, api_id)
        mock_fetch = mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                                  return_value=self._fread(fixture))
        result = Yap.get_movie(api_id, city)
        mock_fetch.assert_called_once_with('https://afisha.yandex.ru/api/events/'
                                           '{}?city={}'.format(api_id, city))
        assert result == {
            'api_id': '5874ea2a685ae0b186614bb5',
            'title': 'Ла-Ла Ленд',
            'title_en': 'La La Land',
            'genres': 'музыкальный, драма, мелодрама, комедия',
            'genres_en': 'Musical, Drama, Romance, Comedy',
            'countries': 'США',
            'cast': 'Райан Гослинг, Эмма Стоун, Финн Уиттрок, Дж.К. Симмонс, Соноя Мидзуно',
            'directors': 'Дэмьен Шазелл',
            'year': 2016,
            'duration': 128,
            'age_restriction': 16,
            'premiere': datetime(2017, 1, 12),
            'kinopoisk_id': 841081,
            'kinopoisk_rating': 8.5,
            'kinopoisk_votes': 42192,
        }

    def test_get_cinema_screenings(self, mocker):
        from datetime import datetime
        fixture = '../fixtures/cinemas/moscow/schedule-561fdfed37753624b592f13f-2017-01-15.json'
        mock_fetch = mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                                  return_value=self._fread(fixture))
        result = Yap.get_cinema_screenings('561fdfed37753624b592f13f', datetime(2017, 1, 15),
                                           'moscow')
        mock_fetch.assert_called_once_with('https://afisha.yandex.ru/api/places/'
                                           '561fdfed37753624b592f13f/schedule_cinema?'
                                           'date=2017-01-15&city=moscow')
        assert len(result) == 12
        assert set([r['cinema_api_id'] for r in result]) == {'561fdfed37753624b592f13f'}
        assert set([r['city'] for r in result]) == {'moscow'}
        assert set([r['date_time'][0:10] for r in result]) == {'2017-01-15'}

        assert sorted(list(result[0].keys())) == ['cinema_api_id', 'city', 'date_time',
                                                  'movie_api_id', 'price_max', 'price_min',
                                                  'ticket_api_id']
        assert [list(r.values()) for r in result] == \
           [['561fdfed37753624b592f13f', '5874ea2a685ae0b186614bb5', None,
             '2017-01-15T11:15:00', 'moscow', None, None],
            ['561fdfed37753624b592f13f', '5874ea2a685ae0b186614bb5', None,
             '2017-01-15T14:00:00', 'moscow', None, None],
            ['561fdfed37753624b592f13f', '5874ea2a685ae0b186614bb5', None,
             '2017-01-15T16:00:00', 'moscow', None, None],
            ['561fdfed37753624b592f13f', '5874ea2a685ae0b186614bb5',
             'Mjg5fDUwNDMzfDQwOTR8MTQ4NDQ5NDIwMDAwMA==', '2017-01-15T18:30:00', 'moscow',
             700.0, 800.0],
            ['561fdfed37753624b592f13f', '5874ea2a685ae0b186614bb5',
             'Mjg5fDUwNDMzfDQwOTV8MTQ4NDQ5NjAwMDAwMA==', '2017-01-15T19:00:00', 'moscow',
             700.0, 700.0],
            ['561fdfed37753624b592f13f', '5874ea2a685ae0b186614bb5',
             'Mjg5fDUwNDMzfDQwOTR8MTQ4NDUwMzIwMDAwMA==', '2017-01-15T21:00:00', 'moscow',
             700.0, 700.0],
            ['561fdfed37753624b592f13f', '5874ea2a685ae0b186614bb5',
             'Mjg5fDUwNDMzfDQwOTV8MTQ4NDUwNTAwMDAwMA==', '2017-01-15T21:30:00', 'moscow',
             700.0, 700.0],
            ['561fdfed37753624b592f13f', '5874ea2a685ae0b186614bb5',
             'Mjg5fDUwNDMzfDQwOTV8MTQ4NDUxMzcwMDAwMA==', '2017-01-15T23:55:00', 'moscow',
             450.0, 450.0],
            ['561fdfed37753624b592f13f', '581aa06f9c183f11f21b5e13',
             'Mjg5fDUxNzk2fDQwOTV8MTQ4NDQ2MTIwMDAwMA==', '2017-01-15T09:20:00', 'moscow',
             200.0, 200.0],
            ['561fdfed37753624b592f13f', '5852bab76ee3daff5c975610',
             'Mjg5fDQ4OTY2fDQwOTR8MTQ4NDQ2MDYwMDAwMA==', '2017-01-15T09:10:00', 'moscow',
             200.0, 200.0],
            ['561fdfed37753624b592f13f', '5575facfcc1c725c1b9865ee',
             'Mjg5fDUwNDMwfDQwOTR8MTQ4NDQ3NTYwMDAwMA==', '2017-01-15T13:20:00', 'moscow',
             350.0, 350.0],
            ['561fdfed37753624b592f13f', '5575facfcc1c725c1b9865ee',
             'Mjg5fDUwNDMwfDQwOTR8MTQ4NDUxMjgwMDAwMA==', '2017-01-15T23:40:00', 'moscow',
             450.0, 450.0]]

    def test_get_movie_ids(self, mocker):
        fixtures_path = '../fixtures/movies/saint-petersburg/'
        mock_fetch = mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                                  side_effect=[
                                      self._fread(fixtures_path + 'movies-offset000-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset012-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset024-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset036-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset048-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset060-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset072-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset084-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset096-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset108-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset120-limit12.json'),
                                      self._fread(fixtures_path + 'movies-offset132-limit12.json')])
        result = Yap.get_movie_ids('saint-petersburg')
        assert mock_fetch.call_count == 12
        mock_fetch.assert_has_calls(
            [call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=0&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=12&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=24&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=36&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=48&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=60&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=72&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=84&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=96&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=108&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=120&tag=cinema&hasMixed=0&city=saint-petersburg'),
             call('https://afisha.yandex.ru/api/events/actual?limit=12&'
                  'offset=132&tag=cinema&hasMixed=0&city=saint-petersburg'),
             ])

        assert len(result) == 133
        assert result[0] == '5874ea2a685ae0b186614bb5'
        assert result[132] == '5881289fcc1c72d7ab9f3a7c'

    def test_get_cinemas(self, mocker):
        fixtures_path = '../fixtures/cinemas/saint-petersburg/'
        mock_fetch = mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                                  side_effect=[
                                      self._fread(fixtures_path + 'cinemas-offset00-limit20.json'),
                                      self._fread(fixtures_path + 'cinemas-offset20-limit20.json'),
                                      self._fread(fixtures_path + 'cinemas-offset40-limit20.json'),
                                      self._fread(fixtures_path + 'cinemas-offset60-limit20.json')])
        result = Yap.get_cinemas('saint-petersburg')
        assert mock_fetch.call_count == 4
        mock_fetch.assert_has_calls([call('https://afisha.yandex.ru/api/events/cinema/places?'
                                          'limit=20&offset=0&city=saint-petersburg'),
                                     call('https://afisha.yandex.ru/api/events/cinema/places?'
                                          'limit=20&offset=20&city=saint-petersburg'),
                                     call('https://afisha.yandex.ru/api/events/cinema/places?'
                                          'limit=20&offset=40&city=saint-petersburg'),
                                     call('https://afisha.yandex.ru/api/events/cinema/places?'
                                          'limit=20&offset=60&city=saint-petersburg')])
        assert len(result) == 62
        assert result[37] == {
            'api_id': u'580b58f18323013d82c1e980',
            'name': u'Angleterre Cinema Lounge',
            'address': u'ул. Малая Морская, 24, отель «Англетер»',
            'phone': u'+7 (812) 494-59-90, +7 (981) 870-77-57',
            'url': u'http://www.angleterrecinema.ru',
            'metro': u'Адмиралтейская, Садовая, Сенная площадь',
            'city': u'saint-petersburg',
            'latitude': 59.933946,
            'longitude': 30.308878
        }

        assert result[16] == {
            'api_id': u'554b45441f6fd628073eef1b',
            'name': u'Формула Кино Заневский Каскад',
            'address': u'Заневский просп., 67/2, ТК «Заневский Каскад»',
            'phone': u'+7 (800) 250-80-25 (автоинформатор)',
            'url': u'http://www.formulakino.ru/',
            'metro': u'Ладожская, Новочеркасская',
            'city': u'saint-petersburg',
            'latitude': 59.933032,
            'longitude': 30.437617
        }
