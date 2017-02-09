# -*- coding: utf-8 -*-


class TestAppViews(object):
    def test_root(self, client):
        result = client.get('/')
        assert result.status_code == 200
        assert result.get_data().decode('utf-8') == 'Hello, World! тест'

    def test_screenings_empty(self, client, dbsession):
        result = client.get('/screenings')
        assert result.status_code == 200
        assert result.get_data().decode('utf-8') == '0'

    def test_screenings(self, client, dbsession):
        import datetime
        from subscity.models.screening import Screening
        sc1 = Screening(movie_api_id='a', cinema_api_id='b', city='moscow',
                        date_time=datetime.datetime(2016, 1, 3, 6, 20))
        sc2 = Screening(movie_api_id='aa', cinema_api_id='bb', city='moscow',
                        date_time=datetime.datetime(2016, 1, 3, 6, 20))
        dbsession.add(sc1)
        dbsession.add(sc2)
        dbsession.commit()
        result = client.get('/screenings')
        assert result.status_code == 200
        assert result.get_data().decode('utf-8') == '2'
