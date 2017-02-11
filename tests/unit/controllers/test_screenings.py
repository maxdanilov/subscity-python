from datetime import datetime

from subscity.controllers.screenings import ScreeningsController


class TestScreeningsController(object):
    def test_get_for_day_empty(self, mocker):
        from subscity.models.screening import Screening
        mock_get_for_day = mocker.patch.object(Screening, 'get_for_day', return_value=[])
        result = ScreeningsController.get_for_day('fake_date', 'fake_city')
        assert result == []
        mock_get_for_day.assert_called_once_with('fake_date', 'fake_city')

    def test_get_for_day(self, mocker):
        from subscity.models.screening import Screening
        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        s1 = Screening(id=1, cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                       city='moscow', date_time=datetime(2017, 2, 15, 12, 15))
        c1 = Cinema(id=100, api_id='fake_cinema1', name='cinema1', city='moscow')
        m1 = Movie(id=1000, api_id='fake_movie1', title='fake_title1')
        s2 = Screening(id=2, cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='moscow', date_time=datetime(2017, 2, 15, 12, 40), price_min=320)
        c2 = Cinema(id=200, api_id='fake_cinema2', name='cinema2', city='moscow')
        m2 = Movie(id=2000, api_id='fake_movie2', title='fake_title2')

        class Row(object):
            def __init__(self, screening, movie, cinema):
                self.Screening = screening
                self.Movie = movie
                self.Cinema = cinema

        from subscity.models.screening import Screening
        mock_get_for_day = mocker.patch.object(Screening, 'get_for_day')
        mock_get_for_day.return_value = [Row(s1, m1, c1), Row(s2, m2, c2)]
        result = ScreeningsController.get_for_day(datetime(2017, 4, 1), 'fake_city')
        assert result == [{'cinema_id': 100,
                           'cinema_name': 'cinema1',
                           'date_time': '2017-02-15T12:15:00',
                           'id': 1,
                           'movie_id': 1000,
                           'movie_title': 'fake_title1',
                           'price': None,
                           'tickets_url': 'https://afisha.yandex.ru/places/fake_cinema1?'
                                          'city=fake_city&place-schedule-date=2017-04-01'},
                          {'cinema_id': 200,
                           'cinema_name': 'cinema2',
                           'date_time': '2017-02-15T12:40:00',
                           'id': 2,
                           'movie_id': 2000,
                           'movie_title': 'fake_title2',
                           'price': 320,
                           'tickets_url': 'https://afisha.yandex.ru/places/fake_cinema2?'
                                          'city=fake_city&place-schedule-date=2017-04-01'}]

        mock_get_for_day.assert_called_once_with(datetime(2017, 4, 1), 'fake_city')