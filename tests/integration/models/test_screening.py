# -*- coding: utf-8 -*-
from tests.utils import fread


class TestModelScreening(object):
    def test_query_empty_result(self, dbsession):
        from subscity.models.screening import Screening
        result = dbsession.query(Screening).all()
        assert len(result) == 0

    def test_delete(self, dbsession):
        from subscity.models.screening import Screening
        from datetime import datetime
        screening = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                              ticket_api_id='fake_ticket', price_min=400.0, price_max=450,
                              city='moscow', date_time=datetime(2017, 1, 1, 9))
        dbsession.add(screening)
        dbsession.commit()
        assert (dbsession.query(Screening).all()[0] == screening)
        screening.delete()
        assert dbsession.query(Screening).all() == []

    def test_save(self, dbsession):
        from subscity.models.screening import Screening
        from datetime import datetime

        screening = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                              ticket_api_id='fake_ticket', price_min=400.0, price_max=450,
                              city='moscow', date_time=datetime(2017, 1, 1, 9))
        screening.save()

        result = dbsession.query(Screening).all()
        assert len(result) == 1
        assert result[0].to_dict(stringify_datetime=False) == {
            'id': screening.id,
            'cinema_api_id': 'fake_cinema',
            'movie_api_id': 'fake_movie',
            'ticket_api_id': 'fake_ticket',
            'city': 'moscow',
            'date_time':  datetime(2017, 1, 1, 9, 0),
            'price_max': 450,
            'price_min': 400,
            'created_at': screening.created_at,
            'updated_at': screening.updated_at
        }

    def test_clean_nothing_found(self, mocker):
        from subscity.models.screening import Screening
        mock_get = mocker.patch.object(Screening, 'get', return_value=[])
        mock_delete = mocker.patch.object(Screening, 'delete')
        result = Screening.clean('fake_cinema_id', 'fake_movie_id', 'fake_start_day',
                                 'fake_end_day', 'fake_city')
        assert result == 0
        mock_get.assert_called_once_with('fake_cinema_id', 'fake_movie_id', 'fake_start_day',
                                         'fake_end_day', 'fake_city')
        assert not mock_delete.called

    def test_clean(self, mocker):
        from unittest.mock import call
        from subscity.models.screening import Screening
        mock_get = mocker.patch.object(Screening, 'get', return_value=[Screening(),
                                                                       Screening()])
        mock_delete = mocker.patch.object(Screening, 'delete')
        result = Screening.clean('fake_cinema_id', 'fake_movie_id', 'fake_start_day',
                                 'fake_end_day', 'fake_city')
        assert result == 2
        mock_get.assert_called_once_with('fake_cinema_id', 'fake_movie_id', 'fake_start_day',
                                         'fake_end_day', 'fake_city')
        assert mock_delete.call_args_list == [call(), call()]

    def test_get(self, dbsession):
        from subscity.models.screening import Screening
        from datetime import datetime

        sc1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                        ticket_api_id='fake_ticket1', price_min=400.0, price_max=450,
                        city='moscow', date_time=datetime(2017, 1, 1, 9))

        sc2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                        ticket_api_id='fake_ticket2', price_min=400.0, price_max=450,
                        city='paris', date_time=datetime(2017, 1, 2, 2, 31))

        sc3 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie3',
                        ticket_api_id='fake_ticket3', price_min=400.0, price_max=450,
                        city='moscow', date_time=datetime(2017, 1, 1, 9))

        sc4 = Screening(cinema_api_id='fake_cinema3', movie_api_id='fake_movie4',
                        ticket_api_id='fake_ticket4', price_min=400.0, price_max=450,
                        city='london', date_time=datetime(2017, 1, 2, 2, 29))

        dbsession.add(sc1)
        dbsession.add(sc2)
        dbsession.add(sc3)
        dbsession.add(sc4)
        dbsession.commit()

        result1 = Screening.get(cinema_api_id='fake_cinema2')
        assert result1 == [sc3, sc2]

        result2 = Screening.get(movie_api_id='fake_movie3')
        assert result2 == [sc3]

        result3 = Screening.get(start_day=datetime(2017, 1, 1), end_day=datetime(2017, 1, 1))
        assert result3 == []  # end_day is exclusive

        result4 = Screening.get(start_day=datetime(2017, 1, 1))
        assert result4 == [sc1, sc3, sc4, sc2]  # ordered by time

        result5 = Screening.get(start_day=datetime(2017, 1, 1), end_day=datetime(2017, 1, 2))
        assert result5 == [sc1, sc3, sc4]

        result6 = Screening.get(start_day=datetime(2017, 1, 2), end_day=datetime(2017, 1, 3),
                                cinema_api_id='fake_something')
        assert result6 == []

        result7 = Screening.get(city='moscow')
        assert result7 == [sc1, sc3]

        result8 = Screening.get(end_day=datetime(2017, 1, 2))
        assert result8 == [sc1, sc3, sc4]  # ordered by time

    def test_parse_and_save(self, mocker, dbsession):
        from datetime import datetime
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap
        from subscity.models.screening import Screening

        fixture = 'fixtures/cinemas/moscow/schedule-561fdfed37753624b592f13f-2017-01-15.json'
        mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                     return_value=fread(fixture))
        result = Yap.get_cinema_screenings('561fdfed37753624b592f13f', datetime(2017, 1, 15),
                                           'moscow')
        sc1 = Screening(**result[0])
        sc1.save()

        sc2 = Screening(**result[1])
        sc2.save()

        result = dbsession.query(Screening).all()
        assert len(result) == 2

        dict_ = result[0].to_dict()
        created_at = dict_.pop('created_at')
        updated_at = dict_.pop('updated_at')
        assert updated_at > created_at
        assert result == [sc1, sc2]
        assert dict_ == {'cinema_api_id': '561fdfed37753624b592f13f',
                         'city': 'moscow',
                         'date_time': '2017-01-15T11:15:00',
                         'id': sc1.id,
                         'movie_api_id': '5874ea2a685ae0b186614bb5',
                         'price_max': None,
                         'price_min': None,
                         'ticket_api_id': None}
