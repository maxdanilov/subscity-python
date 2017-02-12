# -*- coding: utf-8 -*-

import json

import pytest

parametrize = pytest.mark.parametrize


class TestAppViews(object):
    def test_screenings_date_wrong_arguments(self, client):
        result = client.get('/screenings/wrong_city/date/bad_date')
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['city should be one of: msk, spb',
            'date should be in this format: YYYY-MM-DD']

    def test_screenings_date(self, client, mocker):
        from subscity.controllers.screenings import ScreeningsController
        from datetime import datetime

        mock_get_screenings = mocker.patch.object(ScreeningsController, 'get_for_day',
                                                  return_value=['scr1', 'scr2'])
        result = client.get('/screenings/msk/date/2017-02-28')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['scr1', 'scr2']
        mock_get_screenings.assert_called_once_with(datetime(2017, 2, 28), 'moscow')

    @parametrize('city, cinema_id', [('wrong_city', 'bad_cinema'), ('wrong_city', '0')])
    def test_screenings_cinema_wrong_arguments(self, client, city, cinema_id):
        result = client.get('/screenings/{}/cinema/{}'.format(city, cinema_id))
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['cinema id must be an integer',
            'city should be one of: msk, spb']

    def test_screenings_cinema(self, client, mocker):
        from subscity.controllers.screenings import ScreeningsController
        mock_get_screenings = mocker.patch.object(ScreeningsController, 'get_for_cinema',
                                                  return_value=['scr1', 'scr2'])
        result = client.get('/screenings/msk/cinema/123')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['scr1', 'scr2']
        mock_get_screenings.assert_called_once_with(123, 'moscow')

    @parametrize('city, movie_id', [('wrong_city', 'bad_movie'), ('wrong_city', '0')])
    def test_screenings_movie_wrong_arguments(self, client, city, movie_id):
        result = client.get('/screenings/{}/movie/{}'.format(city, movie_id))
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['city should be one of: msk, spb',
            'movie id must be an integer']

    def test_screenings_movie(self, client, mocker):
        from subscity.controllers.screenings import ScreeningsController
        mock_get_screenings = mocker.patch.object(ScreeningsController, 'get_for_movie',
                                                  return_value=['scr1', 'scr2'])
        result = client.get('/screenings/msk/movie/123')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['scr1', 'scr2']
        mock_get_screenings.assert_called_once_with(123, 'moscow')