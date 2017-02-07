from mock import mock_open, patch, call


class TestScripts(object):
    def test_update_screenings(self, mocker):
        import datetime, time
        from subscity.models.cinema import Cinema
        from subscity.models.screening import Screening
        from subscity.scripts import update_screenings
        from subscity.yandex_afisha_parser import YandexAfishaParser
        from tests.utils import mock_datetime
        from unittest.mock import PropertyMock

        YandexAfishaParser.FETCH_DAYS = PropertyMock(return_value=2)
        mock_sleep = mocker.patch.object(time, 'sleep')
        mock_get_all = mocker.patch.object(Cinema, 'get_all', return_value=[
            Cinema(api_id='api_id1', name='cinema1', city='paris'),
            Cinema(api_id='api_id2', name='cinema2', city='moscow'),
            Cinema(api_id='api_id3', name='cinema3', city='london')])
        mock_get_screenings = mocker.patch.object(YandexAfishaParser, 'get_cinema_screenings',
                                                  side_effect=[
            [{'cinema_api_id': 'cinema1_api', 'movie_api_id': 'movie1', 'city': 'paris',
             'date_time': datetime.datetime(2017, 1, 12, 12, 20)},
             {'cinema_api_id': 'cinema1_api', 'movie_api_id': 'movie2', 'city': 'paris',
              'date_time': datetime.datetime(2017, 1, 12, 20, 30)}],
            [], [], [], [],
            [{'cinema_api_id': 'cinema3_api', 'movie_api_id': 'movie1', 'city': 'london',
             'date_time': datetime.datetime(2017, 1, 13, 10, 10)}] ])
        mock_clean_screenings = mocker.patch.object(Screening, 'clean', side_effect=[
            1, 3, 2, 0, 6, 1, 8
        ])
        mock_save = mocker.patch.object(Screening, 'save')
        mock_saving_init = mocker.patch.object(Screening, '__init__', return_value=None)
        with mock_datetime(datetime.datetime(2017, 1, 12, 9, 26, 0)):
            update_screenings()
        mock_get_all.assert_called_once_with()
        assert mock_clean_screenings.call_args_list == [
            call(end_day=datetime.datetime(2017, 1, 12, 9, 26)),
            call(cinema_api_id='api_id1', end_day=datetime.datetime(2017, 1, 13, 9, 26),
                 start_day=datetime.datetime(2017, 1, 12, 9, 26)),
            call(cinema_api_id='api_id1', end_day=datetime.datetime(2017, 1, 14, 9, 26),
                 start_day=datetime.datetime(2017, 1, 13, 9, 26)),
            call(cinema_api_id='api_id2', end_day=datetime.datetime(2017, 1, 13, 9, 26),
                 start_day=datetime.datetime(2017, 1, 12, 9, 26)),
            call(cinema_api_id='api_id2', end_day=datetime.datetime(2017, 1, 14, 9, 26),
                 start_day=datetime.datetime(2017, 1, 13, 9, 26)),
            call(cinema_api_id='api_id3', end_day=datetime.datetime(2017, 1, 13, 9, 26),
                 start_day=datetime.datetime(2017, 1, 12, 9, 26)),
            call(cinema_api_id='api_id3', end_day=datetime.datetime(2017, 1, 14, 9, 26),
                 start_day=datetime.datetime(2017, 1, 13, 9, 26))]

        assert mock_get_screenings.call_args_list == [
            call('api_id1', datetime.datetime(2017, 1, 12, 9, 26), 'paris'),
            call('api_id1', datetime.datetime(2017, 1, 13, 9, 26), 'paris'),
            call('api_id2', datetime.datetime(2017, 1, 12, 9, 26), 'moscow'),
            call('api_id2', datetime.datetime(2017, 1, 13, 9, 26), 'moscow'),
            call('api_id3', datetime.datetime(2017, 1, 12, 9, 26), 'london'),
            call('api_id3', datetime.datetime(2017, 1, 13, 9, 26), 'london')]

        assert mock_saving_init.call_args_list == [
            call(cinema_api_id='cinema1_api', city='paris',
                 date_time=datetime.datetime(2017, 1, 12, 12, 20), movie_api_id='movie1'),
            call(cinema_api_id='cinema1_api', city='paris',
                 date_time=datetime.datetime(2017, 1, 12, 20, 30), movie_api_id='movie2'),
            call(cinema_api_id='cinema3_api', city='london',
                 date_time=datetime.datetime(2017, 1, 13, 10, 10), movie_api_id='movie1')]

        assert mock_save.call_args_list == [call()] * 3
        assert mock_sleep.call_args_list == [call(1.5)] * 6

    def test_update_cinemas(self, mocker):
        import time
        from subscity.yandex_afisha_parser import YandexAfishaParser
        from subscity.scripts import update_cinemas
        from subscity.models.cinema import Cinema

        mock_sleep = mocker.patch.object(time, 'sleep')
        mock_get_cinemas = mocker.patch.object(YandexAfishaParser, 'get_cinemas',
                                               side_effect=[[{'name': '1'}, {'name': '2'}],
                                                            [{'name': '3'}, {'name': '4'}]])
        mock_cinema_init = mocker.patch.object(Cinema, '__init__', return_value=None)
        mock_cinema_save = mocker.patch.object(Cinema, 'create_or_update')
        update_cinemas()
        assert mock_get_cinemas.call_args_list == [call('moscow'), call('saint-petersburg')]
        assert mock_cinema_init.call_args_list == [call(name='1'), call(name='2'), call(name='3'),
                                                   call(name='4')]
        assert mock_cinema_save.call_args_list == [call()] * 4
        assert mock_sleep.call_args_list == [call(2)] * 2

    def test_update_movies(self, mocker):
        import time
        from subscity.yandex_afisha_parser import YandexAfishaParser
        from subscity.scripts import update_movies
        from subscity.models.movie import Movie
        mock_sleep = mocker.patch.object(time, 'sleep')
        mock_get_movie_ids = mocker.patch.object(
            YandexAfishaParser, 'get_movie_ids',
            side_effect=[['aaa', 'bbb'], ['ccc', 'ddd', 'eee']])
        mock_get_movie = mocker.patch.object(
            YandexAfishaParser, 'get_movie',
            side_effect=[{'api_id': 'aaa', 'title': 'one'},
                         {'api_id': 'bbb', 'title': 'two'},
                         {'api_id': 'ccc', 'title': 'three'},
                         {'api_id': 'ddd', 'title': 'four'},
                         {'api_id': 'eee', 'title': 'five'}])
        mock_movie_init = mocker.patch.object(Movie, '__init__', return_value=None)
        mock_movie_save = mocker.patch.object(Movie, 'save')
        update_movies()
        assert mock_get_movie_ids.call_args_list == [call('moscow'), call('saint-petersburg')]
        assert mock_get_movie.call_args_list == [call('aaa', 'moscow'), call('bbb', 'moscow'),
                                                 call('ccc', 'saint-petersburg'),
                                                 call('ddd', 'saint-petersburg'),
                                                 call('eee', 'saint-petersburg')]
        assert mock_movie_init.call_args_list == [call(api_id='aaa', title='one'),
                                                  call(api_id='bbb', title='two'),
                                                  call(api_id='ccc', title='three'),
                                                  call(api_id='ddd', title='four'),
                                                  call(api_id='eee', title='five')]
        assert mock_movie_save.call_args_list == [call()] * 5
        assert mock_sleep.call_args_list == [call(1.5)] * 5

    def test_update_test_fixtures(self, mocker):
        from subscity.scripts import update_test_fixtures
        mock_update_cinema_fixtures = mocker.patch('subscity.scripts.update_test_cinema_fixtures')
        mock_update_movie_fixtures = mocker.patch('subscity.scripts.update_test_movie_fixtures')
        update_test_fixtures()
        mock_update_cinema_fixtures.assert_called_once_with()
        mock_update_movie_fixtures.assert_called_once_with()

    def test_update_test_cinema_fixtures(self, mocker):
        from subscity.scripts import update_test_cinema_fixtures
        from subscity.yandex_afisha_parser import YandexAfishaParser
        mock_file_open = mock_open()
        mock_urls = mocker.patch.object(YandexAfishaParser, 'url_cinemas',
                                        side_effect=['url1', 'url2', 'url3', 'url4'])
        mock_fetch = mocker.patch.object(YandexAfishaParser, 'fetch',
                                         side_effect=['{"json": 1}', '{"json": 2}', '{"json": 3}',
                                                      '{"json": 4}'])
        with patch('subscity.scripts.open', mock_file_open, create=True):
            update_test_cinema_fixtures()
        assert mock_fetch.call_args_list == [call('url1'), call('url2'), call('url3'), call('url4')]
        assert mock_urls.call_args_list == [
            call(city='saint-petersburg', limit=20, offset=0),
            call(city='saint-petersburg', limit=20, offset=20),
            call(city='saint-petersburg', limit=20, offset=40),
            call(city='saint-petersburg', limit=20, offset=60)]
        assert mock_file_open.call_args_list == [
            call('tests/fixtures/cinemas/saint-petersburg/cinemas-offset00-limit20.json', 'w'),
            call('tests/fixtures/cinemas/saint-petersburg/cinemas-offset20-limit20.json', 'w'),
            call('tests/fixtures/cinemas/saint-petersburg/cinemas-offset40-limit20.json', 'w'),
            call('tests/fixtures/cinemas/saint-petersburg/cinemas-offset60-limit20.json', 'w')]

        assert mock_file_open.mock_calls[2]  == call().write('{\n    "json": 1\n}')
        assert mock_file_open.mock_calls[6]  == call().write('{\n    "json": 2\n}')
        assert mock_file_open.mock_calls[10] == call().write('{\n    "json": 3\n}')
        assert mock_file_open.mock_calls[14] == call().write('{\n    "json": 4\n}')

    def test_update_test_movie_fixtures(self, mocker):
        from subscity.scripts import update_test_movie_fixtures
        from subscity.yandex_afisha_parser import YandexAfishaParser
        mock_file_open = mock_open()
        mock_urls = mocker.patch.object(YandexAfishaParser, 'url_movies',
                                        side_effect=['url1', 'url2', 'url3', 'url4',
                                                     'url5', 'url6', 'url7', 'url8',
                                                     'url9', 'url10', 'url11', 'url12'])
        mock_fetch = mocker.patch.object(YandexAfishaParser, 'fetch',
                                         side_effect=['{"json": 1}', '{"json": 2}', '{"json": 3}',
                                                      '{"json": 4}', '{"json": 5}', '{"json": 6}',
                                                      '{"json": 7}', '{"json": 8}', '{"json": 9}',
                                                      '{"json": 10}', '{"json": 11}',
                                                      '{"json": 12}'])
        with patch('subscity.scripts.open', mock_file_open, create=True):
            update_test_movie_fixtures()
        assert mock_fetch.call_args_list == [call('url1'), call('url2'), call('url3'), call('url4'),
                                             call('url5'), call('url6'), call('url7'), call('url8'),
                                             call('url9'), call('url10'), call('url11'),
                                             call('url12')]
        assert mock_urls.call_args_list == [
            call(city='saint-petersburg', limit=12, offset=0),
            call(city='saint-petersburg', limit=12, offset=12),
            call(city='saint-petersburg', limit=12, offset=24),
            call(city='saint-petersburg', limit=12, offset=36),
            call(city='saint-petersburg', limit=12, offset=48),
            call(city='saint-petersburg', limit=12, offset=60),
            call(city='saint-petersburg', limit=12, offset=72),
            call(city='saint-petersburg', limit=12, offset=84),
            call(city='saint-petersburg', limit=12, offset=96),
            call(city='saint-petersburg', limit=12, offset=108),
            call(city='saint-petersburg', limit=12, offset=120),
            call(city='saint-petersburg', limit=12, offset=132)
        ]
        assert mock_file_open.call_args_list == [
            call('tests/fixtures/movies/saint-petersburg/movies-offset000-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset012-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset024-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset036-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset048-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset060-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset072-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset084-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset096-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset108-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset120-limit12.json', 'w'),
            call('tests/fixtures/movies/saint-petersburg/movies-offset132-limit12.json', 'w')
        ]

        assert mock_file_open.mock_calls[2]  == call().write('{\n    "json": 1\n}')
        assert mock_file_open.mock_calls[6]  == call().write('{\n    "json": 2\n}')
        assert mock_file_open.mock_calls[10] == call().write('{\n    "json": 3\n}')
        assert mock_file_open.mock_calls[14] == call().write('{\n    "json": 4\n}')
        assert mock_file_open.mock_calls[18] == call().write('{\n    "json": 5\n}')
        assert mock_file_open.mock_calls[22] == call().write('{\n    "json": 6\n}')
        assert mock_file_open.mock_calls[26] == call().write('{\n    "json": 7\n}')
        assert mock_file_open.mock_calls[30] == call().write('{\n    "json": 8\n}')
        assert mock_file_open.mock_calls[34] == call().write('{\n    "json": 9\n}')
        assert mock_file_open.mock_calls[38] == call().write('{\n    "json": 10\n}')
        assert mock_file_open.mock_calls[42] == call().write('{\n    "json": 11\n}')
        assert mock_file_open.mock_calls[46] == call().write('{\n    "json": 12\n}')
