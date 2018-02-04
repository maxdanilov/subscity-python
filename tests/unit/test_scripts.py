from mock import call


class TestScripts(object):
    def test_update_screenings(self, mocker):
        import datetime
        from subscity.main import DB
        from subscity.models.screening import Screening
        from subscity.scripts import update_screenings
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap
        from tests.utils import mock_datetime

        mock_clean_screenings = mocker.patch.object(Screening, 'clean', return_value=2)
        mock_get_screenings = mocker.patch.object(Yap, 'get_screenings')
        mock_get_screenings.side_effect = [[{'cinema_api_id': 'aaa', 'movie_api_id': 'bbb'}],
                                           [{'cinema_api_id': 'ccc', 'movie_api_id': 'bbb'},
                                            {'cinema_api_id': 'eee', 'movie_api_id': 'fff'}]]
        mock_screening_init = mocker.patch.object(Screening, '__init__',
                                                  return_value=None)
        mock_bulk_save = mocker.patch.object(DB.session, 'bulk_save_objects')

        with mock_datetime(datetime.datetime(2017, 1, 12, 9, 26, 0)):
            update_screenings()

        assert mock_get_screenings.call_args_list == [call('msk'), call('spb')]
        assert mock_clean_screenings.call_args_list == [call(city='msk'), call(city='spb')]
        assert mock_screening_init.call_args_list == [call(cinema_api_id='aaa', movie_api_id='bbb'),
                                                      call(cinema_api_id='ccc', movie_api_id='bbb'),
                                                      call(cinema_api_id='eee', movie_api_id='fff')]
        assert len(mock_bulk_save.call_args_list) == 2

    def test_update_cinemas(self, mocker):
        from subscity.yandex_afisha_parser import YandexAfishaParser
        from subscity.scripts import update_cinemas
        from subscity.models.cinema import Cinema

        mock_get_cinemas = mocker.patch.object(YandexAfishaParser, 'get_cinemas',
                                               side_effect=[[{'name': '1', 'api_id': 'aaa'},
                                                             {'name': '2', 'api_id': 'bbb'}],
                                                            [{'name': '3', 'api_id': 'ccc'},
                                                             {'name': '4', 'api_id': 'ddd'}]])
        mock_cinema_init = mocker.patch.object(Cinema, '__init__', return_value=None)
        mock_cinema_save = mocker.patch.object(Cinema, 'create_or_update')

        update_cinemas()

        assert mock_get_cinemas.call_args_list == [call('msk'), call('spb')]
        assert mock_cinema_init.call_args_list == [call(name='1', api_id='aaa'),
                                                   call(name='2', api_id='bbb'),
                                                   call(name='3', api_id='ccc'),
                                                   call(name='4', api_id='ddd')]
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
        mock_update_screening_fixtures = mocker.patch('subscity.scripts.'
                                                      'update_test_screening_fixtures')

        update_test_fixtures()

        mock_update_cinema_fixtures.assert_called_once_with()
        mock_update_movie_fixtures.assert_called_once_with()
        mock_update_screening_fixtures.assert_called_once_with()

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

    def test_update_test_screening_fixtures(self, mocker):
        from subscity.scripts import update_test_screening_fixtures
        mock_move = mocker.patch('shutil.copy2', return_value=None)
        update_test_screening_fixtures()
        mock_move.assert_called_once_with(
            '/tmp/subscity_afisha_files/afisha_files/spb/cinema/bilet.xml',
            'tests/fixtures/screenings/spb/bilet.xml'
        )
