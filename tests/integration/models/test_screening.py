# -*- coding: utf-8 -*-
import pytest
from datetime import datetime

from subscity.models.screening import Screening
from tests.utils import fread


parametrize = pytest.mark.parametrize


class TestModelScreening(object):
    def test_query_empty_result(self, dbsession):
        result = dbsession.query(Screening).all()
        assert len(result) == 0

    def test_delete(self, dbsession):
        screening = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                              ticket_api_id='fake_ticket', price_min=400.0, price_max=450,
                              city='moscow', date_time=datetime(2017, 1, 1, 9))
        dbsession.add(screening)
        dbsession.commit()
        assert (dbsession.query(Screening).all()[0] == screening)
        screening.delete()
        assert dbsession.query(Screening).all() == []

    def test_insert_duplicate(self, dbsession):
        import pytest
        from sqlalchemy.exc import IntegrityError
        s1 = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                       ticket_api_id='fake_ticket', city='moscow',
                       date_time=datetime(2017, 1, 1, 9))
        s2 = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                       ticket_api_id='fake_ticket2', city='moscow',
                       date_time=datetime(2017, 1, 1, 9))
        dbsession.add(s1)
        dbsession.commit()
        dbsession.add(s2)

        with pytest.raises(IntegrityError) as excinfo:
            dbsession.commit()
        assert "Duplicate entry" in str(excinfo.value)

    def test_save(self, dbsession):
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
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

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
        assert updated_at >= created_at
        # assert result == [sc1, sc2]
        dict2_ = result[1].to_dict()
        created_at2 = dict2_.pop('created_at')
        updated_at2 = dict2_.pop('updated_at')
        assert updated_at2 >= created_at2
        assert dict_ == {'cinema_api_id': '561fdfed37753624b592f13f',
                         'city': 'moscow',
                         'date_time': '2017-01-15T11:15:00',
                         'id': sc1.id,
                         'movie_api_id': '5874ea2a685ae0b186614bb5',
                         'price_max': None,
                         'price_min': None,
                         'ticket_api_id': None}
        assert dict2_ == {'cinema_api_id': '561fdfed37753624b592f13f',
                          'city': 'moscow',
                          'date_time': '2017-01-15T14:00:00',
                          'id': sc2.id,
                          'movie_api_id': '5874ea2a685ae0b186614bb5',
                          'price_max': None,
                          'price_min': None,
                          'ticket_api_id': None}

    def test_get_for_movie_empty(self, dbsession):
        result = Screening.get_for_movie(123456, 'moscow')
        assert result == []

    def test_get_for_movie(self, dbsession):
        from subscity.models.movie import Movie
        from subscity.models.cinema import Cinema
        m1 = Movie(api_id='fake_movie1', title='fake_title1')
        m2 = Movie(api_id='fake_movie2', title='fake_title2')
        dbsession.add(m1)
        dbsession.add(m2)
        dbsession.commit()

        c1 = Cinema(api_id='fake_cinema1', name='cinema1', city='saint-petersburg')
        c2 = Cinema(api_id='fake_cinema2', name='cinema2', city='moscow')
        dbsession.add(c1)
        dbsession.add(c2)
        dbsession.commit()

        # different city
        s1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                       city='saint-petersburg', date_time=datetime(2017, 2, 15, 12, 15))
        # our guy
        s2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='moscow', date_time=datetime(2017, 2, 15, 12, 15))
        # different movie
        s3 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                       city='moscow', date_time=datetime(2017, 2, 16, 12, 15))
        # also our guy
        s4 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie2',
                       city='moscow', date_time=datetime(2017, 2, 18, 12, 15))
        dbsession.add(s1)
        dbsession.add(s2)
        dbsession.add(s3)
        dbsession.add(s4)
        dbsession.commit()

        result = Screening.get_for_movie(m2.id, 'moscow')
        assert result == [(s2, m2, c2), (s4, m2, c1)]

    def test_get_for_cinema_empty(self, dbsession):
        result = Screening.get_for_cinema(123456, 'moscow')
        assert result == []

    def test_get_for_cinema(self, dbsession):
        from subscity.models.movie import Movie
        from subscity.models.cinema import Cinema
        m1 = Movie(api_id='fake_movie1', title='fake_title1')
        m2 = Movie(api_id='fake_movie2', title='fake_title2')
        dbsession.add(m1)
        dbsession.add(m2)
        dbsession.commit()

        c1 = Cinema(api_id='fake_cinema1', name='cinema1', city='saint-petersburg')
        c2 = Cinema(api_id='fake_cinema2', name='cinema2', city='moscow')
        dbsession.add(c1)
        dbsession.add(c2)
        dbsession.commit()

        # different city
        s1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                       city='saint-petersburg', date_time=datetime(2017, 2, 15, 12, 15))
        # our guy
        s2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='moscow', date_time=datetime(2017, 2, 15, 12, 15))
        # different cinema
        s3 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie2',
                       city='moscow', date_time=datetime(2017, 2, 16, 12, 15))
        # also our guy
        s4 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie1',
                       city='moscow', date_time=datetime(2017, 2, 18, 12, 15))
        dbsession.add(s1)
        dbsession.add(s2)
        dbsession.add(s3)
        dbsession.add(s4)
        dbsession.commit()

        result = Screening.get_for_cinema(c2.id, 'moscow')
        assert result == [(s2, m2, c2), (s4, m1, c2)]

    def test_get_for_day_empty(self, dbsession):
        result = Screening.get_for_day(datetime(2017, 2, 15), 'moscow')
        assert result == []

    def test_get_for_day(self, dbsession):
        from subscity.models.movie import Movie
        from subscity.models.cinema import Cinema

        m1 = Movie(api_id='fake_movie1', title='fake_title1')
        m2 = Movie(api_id='fake_movie2', title='fake_title2')
        m3 = Movie(api_id='fake_movie3', title='fake_title3')
        dbsession.add(m1)
        dbsession.add(m2)
        dbsession.add(m3)
        dbsession.commit()

        c1 = Cinema(api_id='fake_cinema1', name='cinema1', city='saint-petersburg')
        c2 = Cinema(api_id='fake_cinema2', name='cinema2', city='moscow')
        c3 = Cinema(api_id='fake_cinema3', name='cinema3', city='moscow')
        dbsession.add(c1)
        dbsession.add(c2)
        dbsession.add(c3)
        dbsession.commit()
        # different city
        s1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                       city='saint-petersburg', date_time=datetime(2017, 2, 15, 12, 15))
        # our guy
        s2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='moscow', date_time=datetime(2017, 2, 15, 12, 15))
        # different day
        s3 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='moscow', date_time=datetime(2017, 2, 16, 12, 15))
        # doesn't have a cinema
        s4 = Screening(cinema_api_id='fake_cinema11', movie_api_id='fake_movie2',
                       city='moscow', date_time=datetime(2017, 2, 15, 20, 0))
        # doesn't have a movie
        s5 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie11',
                       city='moscow', date_time=datetime(2017, 2, 15, 21, 15))
        # also our guy
        s6 = Screening(cinema_api_id='fake_cinema3', movie_api_id='fake_movie3',
                       city='moscow', date_time=datetime(2017, 2, 16, 1, 50))

        dbsession.add(s1)
        dbsession.add(s2)
        dbsession.add(s3)
        dbsession.add(s4)
        dbsession.add(s5)
        dbsession.add(s6)
        dbsession.commit()

        result = Screening.get_for_day(datetime(2017, 2, 15, 23, 55), 'moscow')
        assert result == [(s2, m2, c2), (s6, m3, c3)]

    @parametrize('date_time, day', [(datetime(2017, 2, 16, 10, 50), datetime(2017, 2, 16)),
                                    (datetime(2017, 2, 17, 2, 30), datetime(2017, 2, 16)),
                                    (datetime(2017, 2, 17, 2, 31), datetime(2017, 2, 17))])
    def test_property_day(self, date_time, day):
        screening = Screening(cinema_api_id='fake_cinema3', movie_api_id='fake_movie3',
                              city='moscow', date_time=date_time)
        assert screening.day == day
