from subscity.controllers.cinemas import CinemasController


class TestCinemasController(object):
    def test_get_cinemas_empty(self, mocker):
        from subscity.models.screening import Screening
        from subscity.models.cinema import Cinema

        fake_cinema_movies_ids = []
        mock_get_movies_cinemas = mocker.patch.object(Screening, 'get_movies_cinemas',
                                                      return_value=fake_cinema_movies_ids)
        mock_get_by_ids = mocker.patch.object(Cinema, 'get_by_ids',
                                              return_value='cinemas')
        mock_render = mocker.patch.object(CinemasController, 'render_cinemas',
                                          return_value='rendered')
        result = CinemasController.get_cinemas('moscow')
        mock_get_movies_cinemas.assert_called_once_with('moscow')
        mock_get_by_ids.assert_called_once_with([])
        mock_render.assert_called_once_with('cinemas', fake_cinema_movies_ids)
        assert result == 'rendered'

    def test_get_cinemas(self, mocker):
        from subscity.models.screening import Screening
        from subscity.models.cinema import Cinema

        class Row(object):
            def __init__(self, cinema_id, movie_id):
                self.cinema_id = cinema_id
                self.movie_id = movie_id

        fake_cinema_movies_ids = [Row('c1', 'm1'),
                                  Row('c2', 'm2'),
                                  Row('c2', 'm1')]
        mock_get_movies_cinemas = mocker.patch.object(Screening, 'get_movies_cinemas',
                                                      return_value=fake_cinema_movies_ids)
        mock_get_by_ids = mocker.patch.object(Cinema, 'get_by_ids',
                                              return_value=['cinema1', 'cinema2'])
        mock_render = mocker.patch.object(CinemasController, 'render_cinemas',
                                          return_value=['result1', 'result2'])
        result = CinemasController.get_cinemas('moscow')
        mock_get_movies_cinemas.assert_called_once_with('moscow')
        mock_get_by_ids.assert_called_once_with(['c1', 'c2'])
        mock_render.assert_called_once_with(['cinema1', 'cinema2'], fake_cinema_movies_ids)
        assert result == ['result1', 'result2']

    def test_render_cinemas_empty(self):
        result = CinemasController.render_cinemas([], [])
        assert result == []

    def test_render_cinemas(self):
        from subscity.models.cinema import Cinema
        from decimal import Decimal

        class Row(object):
            def __init__(self, cinema_id, movie_id):
                self.cinema_id = cinema_id
                self.movie_id = movie_id

        c1 = Cinema(id=1, city='moscow', name='Нуово Синема Парадизо',
                    address='ул. Тверская, 21', metro='Пушкинская, Чеховская, Тверская',
                    latitude=Decimal(55.0), longitude=Decimal(37.0),
                    phone='+7 499 123 45 67, +7 499 132 66 53',
                    url='http://nuovocinema.ru, https://cinemaworld.ru')
        c2 = Cinema(id=2, city='moscow', name='Odeon Palace')

        cinema_movies_ids = [Row(cinema_id=1, movie_id=3),
                             Row(cinema_id=2, movie_id=4),
                             Row(cinema_id=2, movie_id=5)]
        cinemas = [c1, c2]

        result = CinemasController.render_cinemas(cinemas, cinema_movies_ids)
        assert result == [
            {
                'id': 1,
                'location':
                    {
                        'address': {
                            'ru': 'ул. Тверская, 21',
                            'en': 'ul. Tverskaja, 21'},
                        'metro': {
                            'ru': ['Пушкинская', 'Чеховская', 'Тверская'],
                            'en': ['Pushkinskaja', 'Chehovskaja', 'Tverskaja']},
                        'longitude': 37.0,
                        'latitude': 55.0
                    },
                'name':
                    {'ru': 'Нуово Синема Парадизо',
                     'en': 'Nuovo Sinema Paradizo'},
                'movies': [3],
                'movies_count': 1,
                'phones': ['+7 499 123 45 67', '+7 499 132 66 53'],
                'urls': ['http://nuovocinema.ru', 'https://cinemaworld.ru']
            },
            {
                'id': 2,
                'location':
                    {
                        'address': {'ru': None, 'en': None},
                        'metro': {'ru': None, 'en': None},
                        'longitude': None,
                        'latitude': None},
                'name':
                    {'ru': 'Odeon Palace',
                     'en': 'Odeon Palace'},
                'movies': [4, 5],
                'movies_count': 2,
                'phones': None,
                'urls': None
             }
        ]
