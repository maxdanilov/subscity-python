# -*- coding: utf-8 -*-

from datetime import datetime
import os

import pytest
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

parametrize = pytest.mark.parametrize


class TestYandexAfishaParser(object):
    def _fread(self, fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    def test_url_tickets(self):
        import datetime
        result = Yap.url_tickets('cinema_api_id', 'city_name', datetime.datetime(2017, 2, 28))
        assert result == "https://afisha.yandex.ru/places/cinema_api_id?city=city_name" \
                         "&place-schedule-date=2017-02-28"

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
                return b'fake-val'

        mock_url_open = mocker.patch('urllib.request.urlopen', return_value=UrlOpenResultFake())
        assert Yap.fetch('some-url') == 'fake-val'
        mock_url_open.assert_called_once_with('some-url')

    @parametrize('input_, output', [({}, None),
                                    ({'release_date': ''}, None),
                                    ({'release_date': '2018-01-12 00:00:00'},
                                     datetime(2018, 1, 12))])
    def test_get_premiere(self, input_, output):
        assert Yap._get_premiere(input_) == output

    @parametrize('input_, output', [({}, None),
                                    ({'du': [115, 115]}, 115),
                                    ({'du': [116]}, 116)])
    def test_get_duration(self, input_, output):
        assert Yap._get_duration(input_) == output

    @parametrize('input_, output', [({}, None),
                                    ({'y': '2017'}, 2017),
                                    ({'y': 2016}, 2016)])
    def test_get_year(self, input_, output):
        assert Yap._get_year(input_) == output

    @parametrize('input_, output', [({}, None),
                                    ({'coid': '5555'}, 5555),
                                    ({'coid': ['7777', '7777']}, 7777)])
    def test_get_kinopoisk_id(self, input_, output):
        assert Yap._get_kinopoisk_id(input_) == output

    @parametrize('input_, output', [
        ({}, None),
        ({'mm': {'s': {'#text': 'Арбатская'}}}, 'Арбатская'),
        ({'mm': {'s': [{'#text': 'Смоленская'}, {'#text': 'Кропоткинская'}]}},
         'Смоленская, Кропоткинская')])
    def test_get_metro(self, input_, output):
        assert Yap._get_metro(input_) == output

    def test_get_genre(self):
        assert Yap._get_genre('') == ''
        assert Yap._get_genre('драма') == 'драма'
        assert Yap._get_genre('авторское кино') == 'артхаус'
        assert Yap._get_genre('документальное кино') == 'документальный'
        assert Yap._get_genre('музыка народов мира') == 'музыкальный'
        assert Yap._get_genre('короткометражный фильм') == 'короткометражный'
        assert Yap._get_genre('семейное кино') == 'семейный'
        assert Yap._get_genre('фильм-нуар') == 'нуар'

    @parametrize('input_, output',
                 [({}, None),
                  ({'g': None}, None),
                  ({'g': 'авторское кино, драма, фильм-нуар'}, 'артхаус, драма, нуар')])
    def test_get_genres(self, input_, output):
        assert Yap._get_genres(input_) == output

    @parametrize('city', ['spb'])
    def test_get_movies(self, city, mocker):
        from datetime import datetime
        fixture = '../../tests/fixtures/movies/{city}/events.xml'.format(city=city)
        mock_read = mocker.patch('subscity.yandex_afisha_parser.read_file',
                                 return_value=self._fread(fixture))
        result = Yap.get_movies(city)
        mock_read.assert_called_once_with('/tmp/subscity_afisha_files/afisha_files/'
                                          '{city}/cinema/events.xml'.format(city=city))

        assert len(result) == 151
        expected = {
            'api_id': '56f38372cc1c7224437a4ecc',
            'cast': 'Фрэнсис МакДорманд, Вуди Харрельсон, Сэм Рокуэлл, Джон Хоукс, Питер '
                    'Динклэйдж, Калеб Лэндри Джонс, Лукас Хеджес, Эбби Корниш, Керри '
                    'Кондон, Даррел Бритт-Гибсон',
            'countries': 'Великобритания, США',
            'description': 'Спустя несколько месяцев после убийства дочери Милдред Хейс '
                           'преступники так и не найдены. Отчаявшаяся женщина решается на '
                           'смелый шаг, арендуя на въезде в город три биллборда с '
                           'посланием к авторитетному главе полиции Уильяму Уиллоуби. '
                           'Когда в ситуацию оказывается втянут еще и заместитель шерифа, '
                           'инфантильный маменькин сынок со склонностью к насилию, офицер '
                           'Диксон, борьба между Милдред и властями города только '
                           'усугубляется.\n'
                           '\n'
                           'Премия Голливудской ассоциации иностранной прессы «Золотой '
                           'глобус» (2017) в категориях «Лучший фильм — драма», «Лучшая '
                           'актриса в драматическом фильме» (Фрэнсис Макдорманд), «Лучший '
                           'актёр второго плана» (Сэм Рокуэлл), «Лучший сценарий» (Мартин '
                           'Макдона), номинация на премию за режиссуру и музыку. Премия '
                           'Ассоциации кинокритиков США (2018) в категории «Лучшая '
                           'актриса» (Фрэнсис Макдорманд), актёру второго плана (Сэм '
                           'Рокуэлл) и за актёрский ансамбль. Номинация на премию Гильдии '
                           'продюсеров США (2018) в категории «Лучший фильм».',
            'directors': 'Мартин МакДона',
            'duration': 115,
            'genres': 'драма, комедия, артхаус',
            'kinopoisk_id': 944098,
            'poster_url': 'https://avatars.mds.yandex.net/get-afishanew/28638/'
                          'b2823c79fe50ed1ca28cff7abea46f46/orig',
            'premiere': datetime(2018, 2, 1, 0, 0),
            'title': 'Три билборда на границе Эббинга, Миссури',
            'title_en': 'Three Billboards Outside Ebbing, Missouri',
            'year': 2017
        }
        assert result[11] == expected

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

        expected = \
            [{'movie_api_id': '5874ea2a685ae0b186614bb5', 'price_max': None, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': None, 'ticket_api_id': None,
              'date_time': '2017-01-15T11:15:00'},
             {'movie_api_id': '5874ea2a685ae0b186614bb5', 'price_max': None, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': None, 'ticket_api_id': None,
              'date_time': '2017-01-15T14:00:00'},
             {'movie_api_id': '5874ea2a685ae0b186614bb5', 'price_max': None, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': None, 'ticket_api_id': None,
              'date_time': '2017-01-15T16:00:00'},
             {'movie_api_id': '5874ea2a685ae0b186614bb5', 'price_max': 800.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 700.0,
              'ticket_api_id': 'Mjg5fDUwNDMzfDQwOTR8MTQ4NDQ5NDIwMDAwMA==',
              'date_time': '2017-01-15T18:30:00'},
             {'movie_api_id': '5874ea2a685ae0b186614bb5', 'price_max': 700.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 700.0,
              'ticket_api_id': 'Mjg5fDUwNDMzfDQwOTV8MTQ4NDQ5NjAwMDAwMA==',
              'date_time': '2017-01-15T19:00:00'},
             {'movie_api_id': '5874ea2a685ae0b186614bb5', 'price_max': 700.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 700.0,
              'ticket_api_id': 'Mjg5fDUwNDMzfDQwOTR8MTQ4NDUwMzIwMDAwMA==',
              'date_time': '2017-01-15T21:00:00'},
             {'movie_api_id': '5874ea2a685ae0b186614bb5', 'price_max': 700.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 700.0,
              'ticket_api_id': 'Mjg5fDUwNDMzfDQwOTV8MTQ4NDUwNTAwMDAwMA==',
              'date_time': '2017-01-15T21:30:00'},
             {'movie_api_id': '5874ea2a685ae0b186614bb5', 'price_max': 450.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 450.0,
              'ticket_api_id': 'Mjg5fDUwNDMzfDQwOTV8MTQ4NDUxMzcwMDAwMA==',
              'date_time': '2017-01-15T23:55:00'},
             {'movie_api_id': '581aa06f9c183f11f21b5e13', 'price_max': 200.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 200.0,
              'ticket_api_id': 'Mjg5fDUxNzk2fDQwOTV8MTQ4NDQ2MTIwMDAwMA==',
              'date_time': '2017-01-15T09:20:00'},
             {'movie_api_id': '5852bab76ee3daff5c975610', 'price_max': 200.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 200.0,
              'ticket_api_id': 'Mjg5fDQ4OTY2fDQwOTR8MTQ4NDQ2MDYwMDAwMA==',
              'date_time': '2017-01-15T09:10:00'},
             {'movie_api_id': '5575facfcc1c725c1b9865ee', 'price_max': 350.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 350.0,
              'ticket_api_id': 'Mjg5fDUwNDMwfDQwOTR8MTQ4NDQ3NTYwMDAwMA==',
              'date_time': '2017-01-15T13:20:00'},
             {'movie_api_id': '5575facfcc1c725c1b9865ee', 'price_max': 450.0, 'city': 'moscow',
              'cinema_api_id': '561fdfed37753624b592f13f', 'price_min': 450.0,
              'ticket_api_id': 'Mjg5fDUwNDMwfDQwOTR8MTQ4NDUxMjgwMDAwMA==',
              'date_time': '2017-01-15T23:40:00'}]
        assert result == expected

    def test_get_cinemas(self, mocker):
        with open('tests/fixtures/cinemas/spb/places.xml', 'r') as file:
            fixture_contents = file.read()

        mock_read_file = mocker.patch('subscity.yandex_afisha_parser.read_file')
        mock_read_file.return_value = fixture_contents
        result = Yap.get_cinemas('spb')

        mock_read_file.assert_called_once_with('/tmp/subscity_afisha_files/afisha_files'
                                               '/spb/cinema/places.xml')

        assert len(result) == 70
        assert result[57] == {
            'api_id': u'580b58f18323013d82c1e980',
            'name': u'Angleterre Cinema Lounge',
            'address': u'ул. Малая Морская, 24, отель «Англетер»',
            'phone': u'+7 (812) 494-59-90, +7 (981) 870-77-57',
            'url': u'http://www.angleterrecinema.ru',
            'metro': u'Адмиралтейская, Садовая, Сенная площадь',
            'city': u'spb',
            'latitude': 59.933946,
            'longitude': 30.308878
        }

        assert result[17] == {
            'api_id': u'554b45441f6fd628073eef1b',
            'name': u'Формула Кино Заневский Каскад',
            'address': u'Заневский просп., 67/2, ТК «Заневский Каскад»',
            'phone': u'+7 (800) 250-80-25 (автоинформатор)',
            'url': u'http://www.formulakino.ru/',
            'metro': u'Ладожская, Новочеркасская',
            'city': u'spb',
            'latitude': 59.933032,
            'longitude': 30.437617
        }
