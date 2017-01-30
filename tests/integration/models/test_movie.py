from subscity.models.movie import Movie


class TestMovie(object):

    def test_query_empty_result(self, dbsession):
        assert dbsession.query(Movie).all() == []

    def test_get_all_empty(self, dbsession):
        assert Movie.get_all() == []
