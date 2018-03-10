# -*- coding: utf-8 -*-

import json

import pytest

parametrize = pytest.mark.parametrize


class TestAppViews(object):
    def test_get_screenings_date_wrong_arguments(self, client):
        result = client.get('/wrong_city/screenings/date/bad_date')
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['city should be one of: [\'msk\', \'spb\']',
            'date should be in this format: YYYY-MM-DD']

    def test_get_screenings_date(self, client, mocker):
        from subscity.controllers.screenings import ScreeningsController
        from datetime import datetime

        mock_get_screenings = mocker.patch.object(ScreeningsController, 'get_for_day',
                                                  return_value=['scr1', 'scr2'])
        result = client.get('/msk/screenings/date/2017-02-28')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['scr1', 'scr2']
        mock_get_screenings.assert_called_once_with(datetime(2017, 2, 28), 'msk')

    @parametrize('city, cinema_id', [('wrong_city', 'bad_cinema'), ('wrong_city', '0')])
    def test_get_screenings_cinema_wrong_arguments(self, client, city, cinema_id):
        result = client.get('{}/screenings/cinema/{}'.format(city, cinema_id))
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['cinema id must be an integer',
            'city should be one of: [\'msk\', \'spb\']']

    def test_get_screenings_cinema(self, client, mocker):
        from subscity.controllers.screenings import ScreeningsController
        mock_get_screenings = mocker.patch.object(ScreeningsController, 'get_for_cinema',
                                                  return_value=['scr1', 'scr2'])
        result = client.get('msk/screenings/cinema/123')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['scr1', 'scr2']
        mock_get_screenings.assert_called_once_with(123, 'msk')

    @parametrize('city, movie_id', [('wrong_city', 'bad_movie'), ('wrong_city', '0')])
    def test_get_screenings_movie_wrong_arguments(self, client, city, movie_id):
        result = client.get('{}/screenings/movie/{}'.format(city, movie_id))
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['city should be one of: [\'msk\', \'spb\']',
            'movie id must be an integer']

    def test_get_screenings_movie(self, client, mocker):
        from subscity.controllers.screenings import ScreeningsController
        mock_get_screenings = mocker.patch.object(ScreeningsController, 'get_for_movie',
                                                  return_value=['scr1', 'scr2'])
        result = client.get('msk/screenings/movie/123')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['scr1', 'scr2']
        mock_get_screenings.assert_called_once_with(123, 'msk')

    def test_get_cinemas_wrong_arguments(self, client):
        result = client.get('/bad_city/cinemas')
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['city should be one of: [\'msk\', \'spb\']']

    def test_get_cinemas(self, client, mocker):
        from subscity.controllers.cinemas import CinemasController
        mock_get_cinemas = mocker.patch.object(CinemasController, 'get_cinemas',
                                               return_value=['c1', 'c2'])
        result = client.get('/msk/cinemas')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['c1', 'c2']
        mock_get_cinemas.assert_called_once_with('msk')

    def test_get_movies_wrong_arguments(self, client):
        result = client.get('/bad_city/movies')
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['city should be one of: [\'msk\', \'spb\']']

    def test_get_movies(self, client, mocker):
        from subscity.controllers.movies import MoviesController
        mock_get_movies = mocker.patch.object(MoviesController, 'get_movies',
                                              return_value=['m1', 'm2'])
        result = client.get('/msk/movies')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['m1', 'm2']
        mock_get_movies.assert_called_once_with('msk')

    def test_get_movie_wrong_arguments(self, client):
        result = client.get('/bad_city/movies/bad_id')
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['city should be one of: [\'msk\', \'spb\']',
            'movie id must be an integer']

    def test_get_movie_not_found(self, client, mocker):
        from subscity.controllers.movies import MoviesController
        mock_get_movie = mocker.patch.object(MoviesController, 'get_movie',
                                             return_value={})
        result = client.get('/msk/movies/42')
        assert result.status_code == 404
        assert json.loads(result.get_data().decode('utf-8')) == {}
        mock_get_movie.assert_called_once_with('msk', 42)

    def test_get_movie(self, client, mocker):
        from subscity.controllers.movies import MoviesController
        mock_get_movie = mocker.patch.object(MoviesController, 'get_movie',
                                             return_value={'id': 42})
        result = client.get('/msk/movies/42')
        assert result.status_code == 200
        assert json.loads(result.get_data().decode('utf-8')) == {'id': 42}
        mock_get_movie.assert_called_once_with('msk', 42)

    def test_requires_auth_not_authorized(self, client):
        result = client.get('/msk/secret')
        assert result.status_code == 403
        assert json.loads(result.get_data().decode('utf-8')) == {'result': 'not allowed'}

    def test_requires_auth_wrong_token(self, client, dbsession):
        from subscity.models.account import Account
        from subscity.models.account import AccountRole

        account = Account(api_token='sometoken', active=True, name='app',
                          role=AccountRole.API_READ)
        dbsession.add(account)
        dbsession.commit()

        result = client.get('/msk/secret', headers={'Authorization': 'wrong_token'})
        assert result.status_code == 403
        assert json.loads(result.get_data().decode('utf-8')) == {'result': 'not allowed'}

    def test_requires_auth_too_weak_role(self, client, dbsession):
        from subscity.models.account import Account
        from subscity.models.account import AccountRole

        account = Account(api_token='sometoken', active=True, name='app',
                          role=AccountRole.API_READ)
        dbsession.add(account)
        dbsession.commit()

        result = client.get('/msk/secret', headers={'Authorization': 'sometoken'})
        assert result.status_code == 403
        assert json.loads(result.get_data().decode('utf-8')) == {'result': 'not allowed'}

    def test_requires_auth_authorized(self, client, dbsession):
        from subscity.models.account import Account
        from subscity.models.account import AccountRole

        account = Account(api_token='sometoken', active=True, name='app',
                          role=AccountRole.API_WRITE)
        dbsession.add(account)
        dbsession.commit()

        result = client.get('/msk/secret', headers={'Authorization': 'sometoken'})
        assert result.status_code == 200
        assert json.loads(result.get_data().decode('utf-8')) == {'result': 42, 'city': 'msk'}
