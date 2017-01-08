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
                   'https://afisha.yandex.ru/api/places?limit=20&offset=40&'
                   'tag=cinema_theater&city=moscow'),
                  (11, '42', 'saint-petersburg',
                   'https://afisha.yandex.ru/api/places?limit=11&offset=42&'
                   'tag=cinema_theater&city=saint-petersburg')])
    def test_url_places(self, limit, offset, city, expected):
        assert Yap.url_places(limit, offset, city) == expected

    @parametrize('limit, offset, city, expected',
                 [(20, 40, 'moscow',
                   'https://afisha.yandex.ru/api/events/actual?limit=20&offset=40&'
                   'tag=cinema&hasMixed=0&city=moscow'),
                  (11, '42', 'saint-petersburg',
                   'https://afisha.yandex.ru/api/events/actual?limit=11&offset=42&'
                   'tag=cinema&hasMixed=0&city=saint-petersburg')])
    def test_url_movies(self, limit, offset, city, expected):
        assert Yap.url_movies(limit, offset, city) == expected

    def test_url_places_wrong_city(self):
        with pytest.raises(ValueError) as exc:
            Yap.url_places(limit='fake-limit', offset='fake_offset', city='fake_city')
        assert str(exc.value) == "city must be one of ('moscow', 'saint-petersburg')"

    def test_fetch(self, mocker):
        class UrlOpenResultFake(object):
            def read(self):
                return 'fake-val'

        mock_url_open = mocker.patch('urllib.request.urlopen', return_value=UrlOpenResultFake())
        assert Yap.fetch('some-url') == 'fake-val'
        mock_url_open.assert_called_once_with('some-url')

    def test_get_cinemas(self, mocker):
        fixtures_path = 'fixtures/cinemas/saint-petersburg/'
        mock_fetch = mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                                  side_effect=[
                                      self._fread(fixtures_path + 'cinemas-offset00-limit20.json'),
                                      self._fread(fixtures_path + 'cinemas-offset20-limit20.json'),
                                      self._fread(fixtures_path + 'cinemas-offset40-limit20.json'),
                                      self._fread(fixtures_path + 'cinemas-offset60-limit20.json')])
        result = Yap.get_cinemas('saint-petersburg')
        assert mock_fetch.call_count == 4
        mock_fetch.assert_has_calls([call('https://afisha.yandex.ru/api/places?limit=20&offset=0&'
                                          'tag=cinema_theater&city=saint-petersburg'),
                                     call('https://afisha.yandex.ru/api/places?limit=20&offset=20&'
                                          'tag=cinema_theater&city=saint-petersburg'),
                                     call('https://afisha.yandex.ru/api/places?limit=20&offset=40&'
                                          'tag=cinema_theater&city=saint-petersburg'),
                                     call('https://afisha.yandex.ru/api/places?limit=20&offset=60&'
                                          'tag=cinema_theater&city=saint-petersburg')])
        assert len(result) == 70
        assert result[0] == {
            'api_id': u'5735eebb100c0a775703e656',
            'title': u'Angleterre Cinema Lounge',
            'address': u'ул. М. Морская, 24, отель «Англетер»',
            'phone': u'+7 (812) 494-59-90, +7 981-870-77-57',
            'url': u'http://www.angleterrecinema.ru/',
            'metro': u'Адмиралтейская, Садовая, Сенная площадь',
            'city': u'saint-petersburg'
        }

        assert result[60] == {
            'api_id': u'554b45441f6fd628073eef1b',
            'title': u'Формула Кино Заневский Каскад',
            'address': u'Заневский просп., 67/2, ТК «Заневский Каскад»',
            'phone': u'+7 (800) 250-80-25 (автоинформатор)',
            'url': u'http://www.formulakino.ru/',
            'metro': u'Ладожская, Новочеркасская, Проспект Большевиков',
            'city': u'saint-petersburg'
        }
