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
        ({'cast': ', '.join(["a{}".format(x) for x in range(20)])},
         'a0, a1, a2, a3, a4, a5, a6, a7, a8, a9'),
        ({'cast': 'a1'}, 'a1')
    ])
    def test_get_cast(self, input_, output):
        assert Yap._get_cast(input_) == output

    @parametrize('input_, output', [
        ({}, None),
        ({'d': ', '.join(["d{}".format(x) for x in range(20)])}, 'd0, d1, d2, d3, d4'),
        ({'d': 'd1'}, 'd1')
    ])
    def test_get_directors(self, input_, output):
        assert Yap._get_directors(input_) == output

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

    def test_get_screening_time(self):
        from datetime import datetime
        item = {'@time': '2018-12-31T23:00'}
        assert Yap._get_screening_time(item) == datetime(2018, 12, 31, 23, 0)

    @parametrize('input_, output', [({}, None),
                                    ({'@min_price': '27000'}, 270.0)])
    def test_get_screening_price(self, input_, output):
        assert Yap._get_screening_price(input_) == output

    @parametrize('input_, output', [
        ({}, False),
        ({'@language_notes': 'some notes'}, False),
        ({'@language_notes': 'На языке оригинала, с русскими субтитрами'}, True)])
    def test_is_screening_with_subs(self, input_, output):
        assert Yap._is_screening_with_subs(input_) == output

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
