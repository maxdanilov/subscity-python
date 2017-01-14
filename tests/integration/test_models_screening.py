# -*- coding: utf-8 -*-
import os

class TestModelScreening(object):
    def _fread(self, fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    def test_query_empty_result(self, dbsession):
        from subscity.models.screening import Screening
        result = dbsession.query(Screening).all()
        assert len(result) == 0

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

        result3 = Screening.get(day=datetime(2017, 1, 1))
        assert result3 == [sc1, sc3, sc4]

        result4 = Screening.get(day=datetime(2017, 1, 2), cinema_api_id='fake_something')
        assert result4 == []

        result5 = Screening.get(city='moscow')
        assert result5 == [sc1, sc3]

    def test_parse_and_save(self, mocker, dbsession):
        from datetime import datetime
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap
        from subscity.models.screening import Screening

        fixture = '../fixtures/cinemas/moscow/schedule-561fdfed37753624b592f13f-2017-01-15.json'
        mocker.patch('subscity.yandex_afisha_parser.YandexAfishaParser.fetch',
                     return_value=self._fread(fixture))
        result = Yap.get_cinema_screenings('561fdfed37753624b592f13f', datetime(2017, 1, 15),
                                           'moscow')
        sc1 = Screening(**result[0])
        sc1.save()

        sc2 = Screening(**result[1])
        sc2.save()

        dbresult = dbsession.query(Screening).all()

        assert len(dbresult) == 2

        dict_ = dbresult[0].to_dict()
        created_at = dict_.pop('created_at')
        updated_at = dict_.pop('updated_at')
        assert updated_at > created_at
        assert dbresult == [sc1, sc2]
        assert dict_ == {'cinema_api_id': '561fdfed37753624b592f13f',
                         'city': 'moscow',
                         'date_time': '2017-01-15T11:15:00',
                         'id': 6,
                         'movie_api_id': '5874ea2a685ae0b186614bb5',
                         'price_max': None,
                         'price_min': None,
                         'ticket_api_id': None}
