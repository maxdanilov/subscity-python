from subscity.models.movie import Movie
from tests.utils import fread, filter_dict


class TestMovie(object):
    def test_query_empty_result(self, dbsession):
        assert dbsession.query(Movie).all() == []

    def test_get_all_api_ids_empty(self, dbsession):
        result = Movie.get_all_api_ids()
        assert result == []

    def test_get_all_api_ids(self, dbsession):
        import datetime
        m1 = Movie(id=12, api_id='aaa', title='Title A',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 2))
        m2 = Movie(id=13, api_id='bbb', title='Title B',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 2))
        dbsession.add(m1)
        dbsession.add(m2)
        dbsession.commit()
        result = Movie.get_all_api_ids()
        assert result == ['aaa', 'bbb']

    def test_get_by_id_empty(self, dbsession):
        assert Movie.get_by_id(1234) is None

    def test_get_by_id(self, dbsession):
        import datetime
        m1 = Movie(id=12, api_id='aaa', title='Title A',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 2))
        m2 = Movie(id=13, api_id='bbb', title='Title B',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 2))
        dbsession.add(m1)
        dbsession.add(m2)
        dbsession.commit()

        assert Movie.get_by_id(13) == m2

    def test_get_all_empty(self, dbsession):
        assert Movie.get_all() == []

    def test_get_all(self, dbsession):
        import datetime
        m1 = Movie(id=12, api_id='aaa', title='Title A',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 2))
        m2 = Movie(id=13, api_id='bbb', title='Title B',
                   created_at=datetime.datetime(2017, 1, 1),
                   updated_at=datetime.datetime(2017, 1, 2))
        dbsession.add(m1)
        dbsession.add(m2)
        dbsession.commit()
        result = Movie.get_all()
        assert len(result) == 2
        assert result[0] == m1
        assert result[1] == m2

    def test_to_dict(self):
        import datetime

        m = Movie(api_id='deadbeef',
                  title='Название',
                  title_original='Title',
                  country='Франция',
                  created_at=datetime.datetime(2017, 1, 1),
                  updated_at=datetime.datetime(2017, 1, 1))
        assert m.to_dict() == {'api_id': 'deadbeef',
                               'age_restriction': None,
                               'active': None,
                               'cast': None,
                               'country': 'Франция',
                               'created_at': '2017-01-01T00:00:00',
                               'description': None,
                               'description_english': None,
                               'director': None,
                               'duration': None,
                               'genres': None,
                               'hide': None,
                               'id': None,
                               'imdb_id': None,
                               'kinopoisk_id': None,
                               'languages': None,
                               'poster': None,
                               'premiere': None,
                               'title': 'Название',
                               'title_original': 'Title',
                               'updated_at': '2017-01-01T00:00:00',
                               'year': None}


    def test_insert_duplicate_api_id(self, dbsession):
        import pytest
        from sqlalchemy.exc import IntegrityError

        m1 = Movie(api_id='id_1', title='movie1')
        m2 = Movie(api_id='id_1', title='movie2')
        dbsession.add(m1)
        dbsession.commit()

        dbsession.add(m2)
        with pytest.raises(IntegrityError) as excinfo:
            dbsession.commit()
        assert "Duplicate entry" in str(excinfo.value)

    def test_parse_and_create(self, mocker, dbsession):
        from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

        fixture = 'fixtures/movies/spb/events.xml'
        mock_read_file = mocker.patch('subscity.yandex_afisha_parser.read_file',
                                      return_value=fread(fixture))
        result = Yap.get_movies('spb')[0]
        m = Movie(**result)
        m.save()

        result = dbsession.query(Movie).all()
        assert len(result) == 1

        dict_ = result[0].to_dict()
        created_at = dict_.pop('created_at')
        updated_at = dict_.pop('updated_at')
        assert updated_at > created_at
        expected = {
            'api_id': '56f38372cc1c7224437a4ecc',
            'age_restriction': None,
            'active': None,
            'cast': 'Фрэнсис МакДорманд, Вуди Харрельсон, Сэм Рокуэлл, Джон Хоукс, Питер '
                    'Динклэйдж, Калеб Лэндри Джонс, Лукас Хеджес, Эбби Корниш, Керри '
                    'Кондон, Даррел Бритт-Гибсон',
            'country': 'США, Великобритания',
            'description': 'Спустя несколько месяцев после убийства дочери Милдред Хейс преступники'
                           ' так и не найдены. Отчаявшаяся женщина решается на смелый шаг, арендуя '
                           'на въезде в город три биллборда с посланием к авторитетному главе '
                           'полиции Уильяму Уиллоуби. Когда в ситуацию оказывается втянут еще и '
                           'заместитель шерифа, инфантильный маменькин сынок со склонностью к '
                           'насилию, офицер Диксон, борьба между Милдред и властями города только '
                           'усугубляется.\n\nПремия «Оскар» (2018): лучшая женская роль (Фрэнсис '
                           'МакДорманд), мужская роль второго плана (Сэм Рокуэлл), номинации: '
                           'фильм, мужская роль второго плана (Вуди Харрельсон), сценарий, монтаж, '
                           'саундтрек.\nПремия Венецианского кинофестиваля (2017) за лучший '
                           'сценарий, номинация на «Золотого льва».\nПремия Голливудской ассоциации'
                           ' иностранной прессы «Золотой глобус» (2017) в категориях «Лучший фильм '
                           '(драма)», «Лучшая женская роль (драма)» (Фрэнсис Макдорманд), «Лучшая '
                           'мужская роль второго плана» (Сэм Рокуэлл), «Лучший сценарий» (Мартин '
                           'Макдона), номинация на премию за режиссуру и саундтрек.\nПремия Гильдии'
                           ' актёров США (2018): женская роль (Фрэнсис МакДорманд), мужская роль '
                           'второго плана (Сэм Рокуэлл), актёрский состав; номинация за мужскую '
                           'роль второго плана (Вуди Харрельсон).\nПремия Ассоциации кинокритиков '
                           'США (2018) в категории «Лучшая актриса» (Фрэнсис Макдорманд), актёру '
                           'второго плана (Сэм Рокуэлл) и за актёрский ансамбль.\nПриз зрительских'
                           ' симпатий за лучший фильм на международном кинофестивале в '
                           'Сан-Себастьяне (Испания, 2017).\nНоминация на премию Гильдии '
                           'продюсеров США (2018) в категории «Лучший фильм».',
            'description_english': None,
            'director': 'Мартин МакДона',
            'duration': 115,
            'genres': 'артхаус, драма, комедия',
            'hide': False,
            'id': m.id,
            'imdb_id': None,
            'kinopoisk_id': 944098,
            'languages': None,
            'poster': 'https://avatars.mds.yandex.net/get-afishanew/28638/'
                          'b2823c79fe50ed1ca28cff7abea46f46/orig',
            'premiere': '2018-02-01T00:00:00',
            'title': 'Три билборда на границе Эббинга, Миссури',
            'title_original': 'Three Billboards Outside Ebbing, Missouri',
            'year': 2017
        }
        assert dict_ == expected
        mock_read_file.assert_called_once_with('/tmp/subscity_afisha_files/'
                                               'afisha_files/spb/cinema/events.xml')

    def test_get_by_api_ids(self, dbsession):
        m1 = Movie(api_id='fake_movie1', title='title1')
        m2 = Movie(api_id='fake_movie2', title='title2')
        m3 = Movie(api_id='fake_movie3', title='title3')
        [dbsession.add(x) for x in [m1, m2, m3]]
        dbsession.commit()
        result = Movie.get_by_api_ids([m1.api_id, m3.api_id])
        assert result == [m1, m3]

        result2 = Movie.get_by_api_ids([])
        assert result2 == []

    def test_get_hidden_api_ids_empty_db(self, dbsession):
        assert Movie.get_hidden_api_ids() == []

    def test_get_hidden_api_ids_empty_result(self, dbsession):
        m1 = Movie(api_id='fake_movie1', title='title1')
        m2 = Movie(api_id='fake_movie2', title='title2')
        m3 = Movie(api_id='fake_movie3', title='title3')
        [dbsession.add(x) for x in [m1, m2, m3]]
        dbsession.commit()

        assert Movie.get_hidden_api_ids() == []

    def test_get_hidden_api_ids(self, dbsession):
        m1 = Movie(api_id='fake_movie1', title='title1')
        m2 = Movie(api_id='fake_movie2', title='title2', hide=True)
        m3 = Movie(api_id='fake_movie3', title='title3', hide=True)
        [dbsession.add(x) for x in [m1, m2, m3]]
        dbsession.commit()

        assert Movie.get_hidden_api_ids() == ['fake_movie2', 'fake_movie3']