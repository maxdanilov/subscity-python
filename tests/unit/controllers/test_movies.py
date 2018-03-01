from subscity.controllers.movies import MoviesController


class TestMoviesController(object):
    def test_render_movies_empty(self):
        result = MoviesController.render_movies([], [])
        assert result == []

    def test_render_movies(self):
        from subscity.models.movie import Movie
        from datetime import datetime
        m1 = Movie(**{
            'id': 1,
            'api_id': '5874ea2a685ae0b186614bb5',
            'title': 'Ла-Ла Ленд',
            'title_en': 'La La Land',
            'description': 'описание фильма',
            'description_en': 'movie description',
            'genres': 'музыкальный, драма, мелодрама, комедия',
            'genres_en': 'Musical, Drama, Romance, Comedy',
            'countries': 'США',
            'countries_en': 'USA',
            'languages': 'английский, французский',
            'languages_en': 'English, French',
            'cast': 'Райан Гослинг, Эмма Стоун, Финн Уиттрок, Дж.К. Симмонс, Соноя Мидзуно',
            'cast_en': 'Ryan Gosling, Emma Stone, J.K. Simmons',
            'directors': 'Дэмьен Шазелл',
            'directors_en': 'Damien Chazelle',
            'year': 2016,
            'duration': 128,
            'age_restriction': 16,
            'premiere': datetime(2017, 1, 12),
            'kinopoisk_id': 841081,
            'kinopoisk_rating': 8.5,
            'kinopoisk_votes': 42192,
            'imdb_id': 123456,
            'imdb_rating': 8.2,
            'imdb_votes': 126500,
        })

        m2 = Movie(**{
            'id': 2,
            'title': 'Криминальное чтиво',
            'api_id': 'arewecoolvincent'
        })

        m3 = Movie(**{
            'id': 3,
            'title': 'Большой куш',
            'api_id': 'fishchipscupoteabadfoodworseweather'
        })

        m4 = Movie(**{
            'id': 4,
            'title': 'Начало',
            'api_id': 'weneedtogodeeper',
            'hide': True,
        })

        class Row(object):
            def __init__(self, next_screening, screenings, movie_api_id):
                self.next_screening = next_screening
                self.screenings = screenings
                self.movie_api_id = movie_api_id

        movies = [m1, m2, m3, m4]
        movies_api_ids_stats = [Row(next_screening=datetime(2017, 2, 23, 8, 20), screenings=10,
                                    movie_api_id='5874ea2a685ae0b186614bb5'),
                                Row(next_screening=datetime(2017, 2, 20, 9, 15), screenings=1,
                                    movie_api_id='fishchipscupoteabadfoodworseweather'),
                                Row(next_screening=datetime(2017, 2, 19, 18, 20), screenings=5,
                                    movie_api_id='weneedtogodeeper')]
        result = MoviesController.render_movies(movies, movies_api_ids_stats)
        assert result == [
            {'languages':
                 {'ru': ['английский', 'французский'],
                  'en': ['English', 'French']},
             'cast':
                 {'ru': ['Райан Гослинг', 'Эмма Стоун', 'Финн Уиттрок', 'Дж.К. Симмонс',
                         'Соноя Мидзуно'],
                  'en': ['Ryan Gosling', 'Emma Stone', 'J.K. Simmons']},
             'screenings':
                 {'count': 10, 'next': '2017-02-23T08:20:00'},
             'age_restriction': 16,
             'duration': 128,
             'year': 2016,
             'genres':
                 {'ru': ['музыкальный', 'драма', 'мелодрама', 'комедия'],
                  'en': ['Musical', 'Drama', 'Romance', 'Comedy']},
             'title':
                 {'ru': 'Ла-Ла Ленд',
                  'en': 'La La Land'},
             'directors':
                 {'ru': ['Дэмьен Шазелл'],
                  'en': ['Damien Chazelle']},
             'countries':
                 {'ru': ['США'], 'en': ['USA']},
             'id': 1,
             'premiere': "2017-01-12",
             'ratings':
                 {'kinopoisk': {'votes': 42192, 'id': 841081, 'rating': 8.5},
                  'imdb': {'votes': 126500, 'id': 123456, 'rating': 8.2}},
             'description':
                 {'ru': 'описание фильма',
                  'en': 'movie description'}},
            {'languages':
                 {'ru': None, 'en': None},
             'cast': {'ru': None, 'en': None},
             'screenings':
                 {'count': 1, 'next': "2017-02-20T09:15:00"},
             'age_restriction': None,
             'duration': None,
             'year': None,
             'genres':
                 {'ru': None, 'en': None},
             'title': {'ru': 'Большой куш', 'en': None},
             'directors': {'ru': None, 'en': None},
             'countries': {'ru': None, 'en': None},
             'id': 3,
             'premiere': None,
             'ratings':
                 {'kinopoisk': {'votes': None, 'id': None, 'rating': None},
                  'imdb': {'votes': None, 'id': None, 'rating': None}},
             'description': {'ru': None, 'en': None}}]

    def test_get_movie_not_found(self, mocker):
        from subscity.models.movie import Movie
        mock_get_by_id = mocker.patch.object(Movie, 'get_by_id', return_value=None)
        result = MoviesController.get_movie(42)
        assert result == {}
        mock_get_by_id.assert_called_once_with(42)

    def test_get_movie(self, mocker):
        from subscity.models.movie import Movie
        mock_movie = Movie()
        mock_get_by_id = mocker.patch.object(Movie, 'get_by_id', return_value=mock_movie)
        mock_render = mocker.patch.object(MoviesController, 'render_movie', return_value='result')

        result = MoviesController.get_movie(42)
        assert result == 'result'
        mock_get_by_id.assert_called_once_with(42)
        mock_render.assert_called_once_with(mock_movie, None)

    def test_get_movies(self, mocker):
        from subscity.models.screening import Screening
        from subscity.models.movie import Movie
        from datetime import datetime

        class Row(object):
            def __init__(self, next_screening, screenings, movie_api_id):
                self.next_screening = next_screening
                self.screenings = screenings
                self.movie_api_id = movie_api_id

        api_ids_stats = [Row(next_screening=datetime(2017, 2, 23, 8, 20), screenings=10,
                             movie_api_id='api_id1'),
                         Row(next_screening=datetime(2017, 2, 20, 9, 15), screenings=1,
                             movie_api_id='api_id2')]
        mock_get_movie_api_ids = mocker.patch.object(Screening, 'get_movie_api_ids',
                                                     return_value=api_ids_stats)
        mock_get_by_api_ids = mocker.patch.object(Movie, 'get_by_api_ids',
                                                  return_value=['movie1', 'movie2'])
        mock_render = mocker.patch.object(MoviesController, 'render_movies', return_value='result')

        result = MoviesController.get_movies('moscow')
        mock_get_movie_api_ids.assert_called_once_with('moscow')
        mock_get_by_api_ids.assert_called_once_with(['api_id1', 'api_id2'])
        mock_render.assert_called_once_with(['movie1', 'movie2'], api_ids_stats)
        assert result == 'result'
