import pytest
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

parametrize = pytest.mark.parametrize


class TestYandexAfishaParser(object):
    @parametrize('limit, offset, city, expected',
                 [(20, 40, 'moscow',
                   'https://afisha.yandex.ru/api/places?limit=20&offset=40&tag=cinema_theater&city=moscow'),
                  (11, '42', 'saint-petersburg',
                   'https://afisha.yandex.ru/api/places?limit=11&offset=42&tag=cinema_theater&city=saint-petersburg')])
    def test_url_places(self, limit, offset, city, expected):
        assert Yap.url_places(limit, offset, city) == expected

    @parametrize('limit, offset, city, expected',
                 [(20, 40, 'moscow',
                   'https://afisha.yandex.ru/api/events/actual?limit=20&offset=40&tag=cinema&hasMixed=0&city=moscow'),
                  (11, '42', 'saint-petersburg',
                   'https://afisha.yandex.ru/api/events/actual?limit=11&offset=42&tag=cinema&hasMixed=0&city=saint-petersburg')])
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

        mock_url_open = mocker.patch('urllib.urlopen', return_value=UrlOpenResultFake())
        assert Yap.fetch('some-url') == 'fake-val'
        mock_url_open.assert_called_once_with('some-url')
