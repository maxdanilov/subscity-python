# -*- coding: utf-8 -*-

import json


class TestAppViews(object):
    def test_root(self, client):
        result = client.get('/')
        assert result.status_code == 200
        assert result.get_data().decode('utf-8') == 'SubsCity API'

    def test_screenings_wrong_arguments(self, client):
        result = client.get('/screenings/wrong_city/bad_date')
        assert result.status_code == 400
        assert sorted(json.loads(result.get_data().decode('utf-8'))['errors']) == \
           ['city should be one of: msk, spb',
            'date should be in this format: YYYY-MM-DD']

    def test_screenings(self, client, mocker):
        from subscity.controllers.screenings import ScreeningsController
        from datetime import datetime

        mock_get_screenings = mocker.patch.object(ScreeningsController, 'get_for_day',
                                                  return_value=['scr1', 'scr2'])
        result = client.get('/screenings/msk/2017-02-28')
        assert result.status_code == 200
        assert sorted(json.loads(result.get_data().decode('utf-8'))) == ['scr1', 'scr2']
        mock_get_screenings.assert_called_once_with(datetime(2017, 2, 28), 'moscow')
