# -*- coding: utf-8 -*-
import pytest
from datetime import datetime

from subscity.models.screening import Screening
from tests.utils import fread, filter_dict, mock_datetime

parametrize = pytest.mark.parametrize


class TestModelScreening(object):
    def test_query_empty_result(self, dbsession):
        result = dbsession.query(Screening).all()
        assert len(result) == 0

    def test_delete(self, dbsession):
        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        c = Cinema(api_id='fake_cinema', city='msk', name='c1')
        m = Movie(api_id='fake_movie', title='m1')
        [dbsession.add(x) for x in [c, m]]
        dbsession.commit()

        screening = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                              ticket_api_id='fake_ticket', price_min=400.0,
                              city='msk', date_time=datetime(2017, 1, 1, 9))
        dbsession.add(screening)
        dbsession.commit()
        assert (dbsession.query(Screening).all()[0] == screening)
        screening.delete()
        assert dbsession.query(Screening).all() == []

    def test_insert_same_time(self, dbsession):
        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        c = Cinema(api_id='fake_cinema', city='msk', name='c1')
        m = Movie(api_id='fake_movie', title='m1')
        [dbsession.add(x) for x in [c, m]]
        dbsession.commit()

        s1 = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                       ticket_api_id='fake_ticket', city='msk',
                       date_time=datetime(2017, 1, 1, 9))
        s2 = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                       ticket_api_id='fake_ticket2', city='msk',
                       date_time=datetime(2017, 1, 1, 9))

        dbsession.add(s1)
        dbsession.add(s2)
        dbsession.commit()

        assert dbsession.query(Screening).all() == [s1, s2]

    def test_save(self, dbsession):
        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        m = Movie(api_id='fake_movie', title='title')
        c = Cinema(api_id='fake_cinema', city='msk', name='c1')
        [dbsession.add(x) for x in [c, m]]
        dbsession.commit()

        screening = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                              ticket_api_id='fake_ticket', price_min=400.0,
                              city='msk', date_time=datetime(2017, 1, 1, 9))
        screening.save()

        result = dbsession.query(Screening).all()
        assert len(result) == 1
        assert result[0].to_dict(stringify_datetime=False) == {
            'id': screening.id,
            'cinema_api_id': 'fake_cinema',
            'movie_api_id': 'fake_movie',
            'ticket_api_id': 'fake_ticket',
            'city': 'msk',
            'date_time': datetime(2017, 1, 1, 9, 0),
            'price_min': 400,
            'source': None,
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

    def test_clean(self, mocker, dbsession):
        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        c = Cinema(api_id='fake_cinema', city='msk', name='c1')
        m = Movie(api_id='fake_movie', title='m1')
        [dbsession.add(x) for x in [c, m]]
        dbsession.commit()

        s1 = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                       ticket_api_id='fake_ticket', city='msk',
                       date_time=datetime(2017, 1, 1, 9))
        s2 = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                       ticket_api_id='fake_ticket2', city='msk',
                       date_time=datetime(2017, 1, 1, 10))
        s3 = Screening(cinema_api_id='fake_cinema', movie_api_id='fake_movie',
                       ticket_api_id='fake_ticket2', city='msk',
                       date_time=datetime(2017, 1, 1, 11))
        dbsession.add(s1)
        dbsession.add(s2)
        dbsession.add(s3)
        dbsession.commit()

        mock_get = mocker.patch.object(Screening, 'get', return_value=[s1, s3])

        result = Screening.clean('fake_cinema_id', 'fake_movie_id', 'fake_start_day',
                                 'fake_end_day', 'fake_city')

        assert result == 2
        mock_get.assert_called_once_with('fake_cinema_id', 'fake_movie_id', 'fake_start_day',
                                         'fake_end_day', 'fake_city')

        result = dbsession.query(Screening).all()
        assert result == [s2]

    def test_get(self, dbsession):
        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        m1 = Movie(api_id='fake_movie1', title='m1')
        m2 = Movie(api_id='fake_movie2', title='m2')
        m3 = Movie(api_id='fake_movie3', title='m3')
        m4 = Movie(api_id='fake_movie4', title='m4')
        [dbsession.add(x) for x in [m1, m2, m3, m4]]
        dbsession.commit()

        c1 = Cinema(api_id='fake_cinema1', city='msk', name='c1')
        c2 = Cinema(api_id='fake_cinema2', city='prs', name='c2')
        c3 = Cinema(api_id='fake_cinema3', city='lnd', name='c3')
        [dbsession.add(x) for x in [c1, c2, c3]]
        dbsession.commit()

        sc1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                        ticket_api_id='fake_ticket1', price_min=400.0,
                        city='msk', date_time=datetime(2017, 1, 1, 9))

        sc2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                        ticket_api_id='fake_ticket2', price_min=400.0,
                        city='prs', date_time=datetime(2017, 1, 2, 2, 31))

        sc3 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie3',
                        ticket_api_id='fake_ticket3', price_min=400.0,
                        city='msk', date_time=datetime(2017, 1, 1, 9))

        sc4 = Screening(cinema_api_id='fake_cinema3', movie_api_id='fake_movie4',
                        ticket_api_id='fake_ticket4', price_min=400.0,
                        city='lnd', date_time=datetime(2017, 1, 2, 2, 29))
        [dbsession.add(x) for x in [sc1, sc2, sc3, sc4]]
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

        result7 = Screening.get(city='msk')
        assert result7 == [sc1, sc3]

        result8 = Screening.get(end_day=datetime(2017, 1, 2))
        assert result8 == [sc1, sc3, sc4]  # ordered by time

    def test_parse_and_save(self, mocker, dbsession):
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap
        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        fixture = 'fixtures/screenings/spb/bilet.xml'
        mocker.patch('subscity.yandex_afisha_parser.read_file',
                     return_value=fread(fixture))
        result = Yap.get_screenings('spb')
        assert len(result) == 162

        m1 = Movie(api_id=result[0]['movie_api_id'], title='m1')
        m2 = Movie(api_id=result[1]['movie_api_id'], title='m2')
        c = Cinema(api_id=result[0]['cinema_api_id'], name='c1', city='spb')

        [dbsession.add(x) for x in [m1, m2, c]]
        dbsession.commit()

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
        assert dict_ == {'cinema_api_id': '578c15008dabaf9ff14b9048',
                         'city': 'spb',
                         'date_time': '2018-02-04T17:40:00',
                         'id': sc1.id,
                         'movie_api_id': '5575ec34cc1c72361ee31384',
                         'price_min': None,
                         'source': 'yandex',
                         'ticket_api_id': None}
        assert dict2_ == {'cinema_api_id': '578c15008dabaf9ff14b9048',
                          'city': 'spb',
                          'date_time': '2018-02-04T15:00:00',
                          'id': sc2.id,
                          'movie_api_id': '55762ad4cc1c725c189884be',
                          'price_min': None,
                          'source': 'yandex',
                          'ticket_api_id': None}

    @parametrize('date_time, day', [(datetime(2017, 2, 16, 10, 50), datetime(2017, 2, 16)),
                                    (datetime(2017, 2, 17, 2, 30), datetime(2017, 2, 16)),
                                    (datetime(2017, 2, 17, 2, 31), datetime(2017, 2, 17))])
    def test_property_day(self, date_time, day):
        screening = Screening(cinema_api_id='fake_cinema3', movie_api_id='fake_movie3',
                              city='msk', date_time=date_time)
        assert screening.day == day

    def test_get_movie_api_ids_empty(self, dbsession):
        result = Screening.get_movie_api_ids('msk')
        assert result == []

    def test_get_movie_api_ids(self, dbsession):
        import datetime

        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        c1 = Cinema(api_id='fake_cinema1', city='spb', name='c1')
        c2 = Cinema(api_id='fake_cinema2', city='msk', name='c2')
        c3 = Cinema(api_id='fake_cinema3', city='msk', name='c3')
        m1 = Movie(api_id='fake_movie1', title='t1')
        m2 = Movie(api_id='fake_movie2', title='t2')
        m3 = Movie(api_id='fake_movie3', title='t3')

        [dbsession.add(x) for x in [c1, c2, c3, m1, m2, m3]]
        dbsession.commit()

        # passed
        s0 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='msk', date_time=datetime.datetime(2017, 2, 10, 13, 15))
        # different city
        s1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                       city='spb', date_time=datetime.datetime(2017, 2, 15, 12, 15))
        # our guy
        s2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='msk', date_time=datetime.datetime(2017, 2, 15, 13, 15))

        # our guy
        s3 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='msk', date_time=datetime.datetime(2017, 2, 15, 13, 0))
        # our guy
        s4 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie3',
                       city='msk', date_time=datetime.datetime(2017, 2, 16, 20, 0))

        # our guy
        s5 = Screening(cinema_api_id='fake_cinema3', movie_api_id='fake_movie3',
                       city='msk', date_time=datetime.datetime(2017, 2, 16, 21, 0))

        [dbsession.add(x) for x in [s0, s1, s2, s3, s4, s5]]
        dbsession.commit()

        with mock_datetime(mock_utcnow=datetime.datetime(2017, 2, 15, 8, 10)):
            result = Screening.get_movie_api_ids('msk')
        assert result == [(datetime.datetime(2017, 2, 15, 13, 0), 2, 1, 'fake_movie2'),
                          (datetime.datetime(2017, 2, 16, 20, 0), 2, 2, 'fake_movie3')]
        # test that we have a namedtuple, not just a tuple
        assert result[0].next_screening == datetime.datetime(2017, 2, 15, 13, 0)
        assert result[0].screenings == 2
        assert result[0].cinemas == 1
        assert result[0].movie_api_id == 'fake_movie2'

    def test_bulk_save_empty_input(self, dbsession):
        Screening.bulk_save([])
        assert dbsession.query(Screening).all() == []

    def test_bulk_save(self, dbsession):
        import datetime

        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        c1 = Cinema(api_id='fake_cinema1', city='msk', name='c1')
        c2 = Cinema(api_id='fake_cinema2', city='spb', name='c2')
        m1 = Movie(api_id='fake_movie2', title='m2')
        m2 = Movie(api_id='fake_movie3', title='m3')
        [dbsession.add(x) for x in [c1, c2, m1, m2]]
        dbsession.commit()

        s1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie2',
                       city='msk', date_time=datetime.datetime(2017, 2, 15, 13, 0))
        s2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie3',
                       city='msk', date_time=datetime.datetime(2017, 2, 16, 20, 0))
        s3 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie3',
                       city='spb', date_time=datetime.datetime(2017, 2, 16, 21, 0))
        s1.save()

        assert dbsession.query(Screening).all() == [s1]
        Screening.bulk_save([s2, s3])

        result = dbsession.query(Screening).all()
        assert len(result) == 3

        filter_keys = ['cinema_api_id', 'movie_api_id', 'city', 'date_time']
        assert filter_dict(result[0].to_dict(), filter_keys) == {
            'cinema_api_id': 'fake_cinema1',
            'movie_api_id': 'fake_movie2',
            'city': 'msk',
            'date_time': '2017-02-15T13:00:00'
        }

        assert filter_dict(result[1].to_dict(), filter_keys) == {
            'cinema_api_id': 'fake_cinema2',
            'movie_api_id': 'fake_movie3',
            'city': 'msk',
            'date_time': '2017-02-16T20:00:00'
        }

        assert filter_dict(result[2].to_dict(), filter_keys) == {
            'cinema_api_id': 'fake_cinema2',
            'movie_api_id': 'fake_movie3',
            'city': 'spb',
            'date_time': '2017-02-16T21:00:00'
        }

    def test_clean_hidden_empty(self, dbsession):
        assert Screening.clean_hidden('msk') == 0

    def test_clean_hidden(self, dbsession):
        import datetime
        from subscity.models.cinema import Cinema
        from subscity.models.movie import Movie

        m1 = Movie(api_id='fake_movie1', title='title1')
        m2 = Movie(api_id='fake_movie2', title='title2', hide=True)
        m3 = Movie(api_id='fake_movie3', title='title3', hide=True)
        c1 = Cinema(api_id='fake_cinema1', city='msk', name='c1')
        c2 = Cinema(api_id='fake_cinema2', city='msk', name='c2')
        c3 = Cinema(api_id='fake_cinema3', city='spb', name='c3')
        [dbsession.add(x) for x in [m1, m2, m3, c1, c2, c3]]
        dbsession.commit()

        # not a hidden movie
        s1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                       city='msk', date_time=datetime.datetime(2017, 2, 15, 13, 0))
        # will be deleted
        s2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie2',
                       city='msk', date_time=datetime.datetime(2017, 2, 16, 20, 0))
        # a hidden movie but from a different city
        s3 = Screening(cinema_api_id='fake_cinema3', movie_api_id='fake_movie3',
                       city='spb', date_time=datetime.datetime(2017, 2, 16, 21, 0))
        [dbsession.add(s) for s in [s1, s2, s3]]
        dbsession.commit()

        result = Screening.clean_hidden('msk')
        assert result == 1

        screenings = dbsession.query(Screening).all()
        assert [s.id for s in screenings] == [s1.id, s3.id]

    def test_clean_premature_empty(self, dbsession):
        assert Screening.clean_premature('msk') == 0

    def test_clean_premature(self, dbsession):
        import datetime
        from subscity.models.movie import Movie
        from subscity.models.cinema import Cinema

        m1 = Movie(api_id='fake_movie1', title='title1')
        m2 = Movie(api_id='fake_movie2', title='title2')
        m3 = Movie(api_id='fake_movie3', title='title3')
        [dbsession.add(x) for x in [m1, m2, m3]]
        dbsession.commit()

        c1 = Cinema(api_id='fake_cinema1', city='msk', name='C1')
        c2 = Cinema(api_id='fake_cinema2', city='msk', name='C2')
        c3 = Cinema(api_id='fake_cinema3', city='spb', name='C3')
        c4 = Cinema(api_id='fake_cinema4', city='msk', name='C4')
        [dbsession.add(x) for x in [c1, c2, c3, c4]]
        dbsession.commit()

        # a premature screening
        s1 = Screening(cinema_api_id='fake_cinema1', movie_api_id='fake_movie1',
                       city='msk', date_time=datetime.datetime(2018, 6, 6, 0, 1))

        # a premature screening
        s2 = Screening(cinema_api_id='fake_cinema2', movie_api_id='fake_movie1',
                       city='msk', date_time=datetime.datetime(2018, 6, 6, 5, 5))

        # a different city, will be kept
        s3 = Screening(cinema_api_id='fake_cinema3', movie_api_id='fake_movie1',
                       city='spb', date_time=datetime.datetime(2018, 6, 2, 12, 0))

        # will be kept
        s4 = Screening(cinema_api_id='fake_cinema4', movie_api_id='fake_movie2',
                       city='msk', date_time=datetime.datetime(2018, 6, 1, 20, 0))

        [dbsession.add(s) for s in [s1, s2, s3, s4]]
        dbsession.commit()

        with mock_datetime(mock_utcnow=datetime.datetime(2018, 5, 31, 21, 0)):  # midnight msk
            result = Screening.clean_premature('msk')

        assert result == 2

        screenings = dbsession.query(Screening).all()
        assert [s.id for s in screenings] == [s3.id, s4.id]
