from typing import List

from subscity.models.screening import Screening


class CinemasController(object):
    @classmethod
    def get_cinemas(cls, city: str) -> List:
        cinema_movie_ids = Screening.get_movies_cinemas(city)
        cinema_ids = sorted(list(set([r.cinema_id for r in cinema_movie_ids])))
        cinemas = Screening.get_by_ids(cinema_ids)
        return cls.render_cinemas(cinemas, cinema_movie_ids)

    @classmethod
    def render_cinemas(cls, cinemas, cinema_movie_ids):
        result = []
        for cinema in cinemas:
            movie_ids = [r.movie_id for r in cinema_movie_ids if r.cinema_id == cinema.id]
            cinema_dict = \
                {
                    'id': cinema.id,
                    'location': {
                        'address': cinema.address,
                        'metro': cinema.metro.split(', ') if cinema.metro else None,
                        'latitude': cinema.latitude,
                        'longitude': cinema.longitude
                    },
                    'name': cinema.name,
                    'phones': cinema.phone.split(', ') if cinema.phone else None,
                    'urls': cinema.url.split(', ') if cinema.url else None,
                    'movies': movie_ids,
                    'movies_count': len(movie_ids)
                }
            result.append(cinema_dict)
        return result
