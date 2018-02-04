from mock import call


class TestScripts(object):
    def test_update_screenings_cinema(self, mocker):
        from datetime import datetime
        from subscity.scripts import update_screenings_cinema
        from subscity.models.cinema import Cinema
        from subscity.models.screening import Screening
        from subscity.yandex_afisha_parser import YandexAfishaParser

        cinema = Cinema(api_id='api_id1', name='cinema1', city='moscow')
        date = datetime(2017, 2, 10, 9, 55)

        mock_get_screenings = mocker.patch.object(YandexAfishaParser, 'get_cinema_screenings',
                                                  return_value=[
                                                      {'cinema_api_id': 'cinema1_api',
                                                       'movie_api_id': 'movie1', 'city': 'moscow',
                                                       'date_time': datetime(2017, 1, 12, 12, 20)},
                                                      {'cinema_api_id': 'cinema1_api',
                                                       'movie_api_id': 'movie2', 'city': 'moscow',
                                                       'date_time': datetime(2017, 1, 12, 20, 30)}])
        mock_clean_screenings = mocker.patch.object(Screening, 'clean', return_value=5)
        mock_save = mocker.patch.object(Screening, 'save')
        mock_saving_init = mocker.patch.object(Screening, '__init__', return_value=None)

        update_screenings_cinema(cinema, date)

        mock_get_screenings.assert_called_once_with('api_id1', datetime(2017, 2, 10, 9, 55),
                                                    'moscow')
        mock_clean_screenings.assert_called_once_with(cinema_api_id='api_id1',
                                                      end_day=datetime(2017, 2, 11, 9, 55),
                                                      start_day=datetime(2017, 2, 10, 9, 55))
        assert mock_saving_init.call_args_list == [
            call(cinema_api_id='cinema1_api', city='moscow',
                 date_time=datetime(2017, 1, 12, 12, 20), movie_api_id='movie1'),
            call(cinema_api_id='cinema1_api', city='moscow',
                 date_time=datetime(2017, 1, 12, 20, 30), movie_api_id='movie2')]
        assert mock_save.call_args_list == [call()] * 2

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
        cinemas = [Cinema(api_id='api_id1', name='cinema1', city='paris'),
                   Cinema(api_id='api_id2', name='cinema2', city='moscow')]
        mock_get_all = mocker.patch.object(Cinema, 'get_all', return_value=cinemas)
        mock_clean_screenings = mocker.patch.object(Screening, 'clean', return_value=2)
        mock_update_screenings_cinema = mocker.patch('subscity.scripts.update_screenings_cinema')

        with mock_datetime(datetime.datetime(2017, 1, 12, 9, 26, 0)):
            update_screenings()

        mock_get_all.assert_called_once_with()
        mock_clean_screenings.assert_called_once_with(end_day=datetime.datetime(2017, 1, 12, 9, 26))
        assert mock_sleep.call_args_list == [call(1.5)] * 4
        assert mock_update_screenings_cinema.call_args_list == \
               [call(cinemas[0], datetime.datetime(2017, 1, 12, 9, 26, 0)),
                call(cinemas[0], datetime.datetime(2017, 1, 13, 9, 26, 0)),
                call(cinemas[1], datetime.datetime(2017, 1, 12, 9, 26, 0)),
                call(cinemas[1], datetime.datetime(2017, 1, 13, 9, 26, 0))]

    def test_update_screenings_exception(self, mocker):
        import datetime, time
        import traceback
        from subscity.main import DB
        from subscity.models.cinema import Cinema
        from subscity.models.screening import Screening
        from subscity.scripts import update_screenings
        from subscity.yandex_afisha_parser import YandexAfishaParser
        from tests.utils import mock_datetime
        from unittest.mock import PropertyMock

        YandexAfishaParser.FETCH_DAYS = PropertyMock(return_value=2)
        mock_sleep = mocker.patch.object(time, 'sleep')
        cinemas = [Cinema(api_id='api_id1', name='cinema1', city='paris'),
                   Cinema(api_id='api_id2', name='cinema2', city='moscow')]
        mock_get_all = mocker.patch.object(Cinema, 'get_all', return_value=cinemas)
        mock_clean_screenings = mocker.patch.object(Screening, 'clean', return_value=2)
        mock_update_screenings_cinema = mocker.patch('subscity.scripts.update_screenings_cinema',
                                                     side_effect=[ValueError('some error'),
                                                                  None,
                                                                  None,
                                                                  None])
        mock_rollback = mocker.patch.object(DB.session, 'rollback')
        mock_traceback = mocker.patch.object(traceback, 'print_exc')

        with mock_datetime(datetime.datetime(2017, 1, 12, 9, 26, 0)):
            update_screenings()

        mock_rollback.assert_called_once_with()
        mock_traceback.assert_called_once_with()
        mock_get_all.assert_called_once_with()
        mock_clean_screenings.assert_called_once_with(end_day=datetime.datetime(2017, 1, 12, 9, 26))
        assert mock_sleep.call_args_list == [call(1.5)] * 4
        assert mock_update_screenings_cinema.call_args_list == \
               [call(cinemas[0], datetime.datetime(2017, 1, 12, 9, 26, 0)),
                call(cinemas[0], datetime.datetime(2017, 1, 13, 9, 26, 0)),
                call(cinemas[1], datetime.datetime(2017, 1, 12, 9, 26, 0)),
                call(cinemas[1], datetime.datetime(2017, 1, 13, 9, 26, 0))]

    def test_update_cinemas(self, mocker):
        from subscity.yandex_afisha_parser import YandexAfishaParser
        from subscity.scripts import update_cinemas
        from subscity.models.cinema import Cinema

        mock_get_cinemas = mocker.patch.object(YandexAfishaParser, 'get_cinemas',
                                               side_effect=[[{'name': '1'}, {'name': '2'}],
                                                            [{'name': '3'}, {'name': '4'}]])
        mock_cinema_init = mocker.patch.object(Cinema, '__init__', return_value=None)
        mock_cinema_save = mocker.patch.object(Cinema, 'create_or_update')

        update_cinemas()

        assert mock_get_cinemas.call_args_list == [call('msk'), call('spb')]
        assert mock_cinema_init.call_args_list == [call(name='1'), call(name='2'), call(name='3'),
                                                   call(name='4')]
        assert mock_cinema_save.call_args_list == [call()] * 4

    def test_update_movies(self, mocker):
        from subscity.yandex_afisha_parser import YandexAfishaParser
        from subscity.scripts import update_movies
        from subscity.models.movie import Movie

        mock_get_movies = mocker.patch.object(
            YandexAfishaParser, 'get_movies',
            side_effect=[[{'api_id': 'aaa', 'title': 'one'}, {'api_id': 'bbb', 'title': 'two'}],
                         [{'api_id': 'ccc', 'title': 'five'}, {'api_id': 'ddd', 'title': 'four'},
                          {'api_id': 'aaa', 'title': 'one'}]])

        mock_movie_init = mocker.patch.object(Movie, '__init__', return_value=None)
        mock_movie_save = mocker.patch.object(Movie, 'save')
        mock_get_movie_ids_db = mocker.patch.object(Movie, 'get_all_api_ids',
                                                    side_effect=[['ccc'],
                                                                 ['ccc', 'aaa', 'bbb']])

        update_movies()

        assert mock_get_movies.call_args_list == [call('msk'), call('spb')]
        assert mock_movie_init.call_args_list == [call(api_id='aaa', title='one'),
                                                  call(api_id='bbb', title='two'),
                                                  call(api_id='ddd', title='four')]
        assert mock_movie_save.call_args_list == [call()] * 3
        assert mock_get_movie_ids_db.call_args_list == [call(), call()]

    def test_update_movies_exception(self, mocker):
        import traceback
        from subscity.main import DB
        from subscity.yandex_afisha_parser import YandexAfishaParser
        from subscity.scripts import update_movies
        from subscity.models.movie import Movie

        mock_get_movies = mocker.patch.object(
            YandexAfishaParser, 'get_movies',
            side_effect=[[{'api_id': 'aaa', 'title': 'one'}, {'api_id': 'bbb', 'title': 'two'}],
                         [{'api_id': 'ccc', 'title': 'five'}, {'api_id': 'ddd', 'title': 'four'},
                          {'api_id': 'aaa', 'title': 'one'}]])

        mock_movie_init = mocker.patch.object(Movie, '__init__', return_value=None)
        mock_movie_save = mocker.patch.object(Movie, 'save',
                                              side_effect=[None, ValueError('save error'), None])
        mock_get_movie_ids_db = mocker.patch.object(Movie, 'get_all_api_ids',
                                                    side_effect=[['ccc'],
                                                                 ['ccc', 'aaa', 'bbb']])
        mock_rollback = mocker.patch.object(DB.session, 'rollback')
        mock_traceback = mocker.patch.object(traceback, 'print_exc')

        update_movies()

        assert mock_get_movies.call_args_list == [call('msk'), call('spb')]
        assert mock_movie_init.call_args_list == [call(api_id='aaa', title='one'),
                                                  call(api_id='bbb', title='two'),
                                                  call(api_id='ddd', title='four')]
        assert mock_movie_save.call_args_list == [call()] * 3
        assert mock_get_movie_ids_db.call_args_list == [call(), call()]
        mock_rollback.assert_called_once_with()
        mock_traceback.assert_called_once_with()

    def test_update_test_fixtures(self, mocker):
        from subscity.scripts import update_test_fixtures
        mock_update_cinema_fixtures = mocker.patch('subscity.scripts.update_test_cinema_fixtures')
        mock_update_movie_fixtures = mocker.patch('subscity.scripts.update_test_movie_fixtures')
        update_test_fixtures()
        mock_update_cinema_fixtures.assert_called_once_with()
        mock_update_movie_fixtures.assert_called_once_with()

    def test_update_test_cinema_fixtures(self, mocker):
        from subscity.scripts import update_test_cinema_fixtures
        mock_move = mocker.patch('shutil.copy2', return_value=None)
        update_test_cinema_fixtures()
        mock_move.assert_called_once_with(
            '/tmp/subscity_afisha_files/afisha_files/spb/cinema/places.xml',
            'tests/fixtures/cinemas/spb/places.xml'
        )

    def test_update_test_movie_fixtures(self, mocker):
        from subscity.scripts import update_test_movie_fixtures
        mock_move = mocker.patch('shutil.copy2', return_value=None)
        update_test_movie_fixtures()
        mock_move.assert_called_once_with(
            '/tmp/subscity_afisha_files/afisha_files/spb/cinema/events.xml',
            'tests/fixtures/movies/spb/events.xml'
        )
