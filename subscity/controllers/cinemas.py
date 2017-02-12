from typing import List

from subscity.models.cinema import Cinema
from subscity.models.screening import Screening


class CinemasController(object):
    @classmethod
    def get_cinemas(cls, city: str) -> List:
        cinema_movie_ids = Screening.get_movies_cinemas(city)
        cinema_ids = sorted(list(set([r.cinema_id for r in cinema_movie_ids])))
        cinemas = Cinema.get_by_ids(cinema_ids)
        return cls.render_cinemas(cinemas, cinema_movie_ids)

    @classmethod
    def render_cinemas(cls, cinemas: List, cinema_movie_ids: List) -> List:
        result = []
        for cinema in cinemas:
            movie_ids = [r.movie_id for r in cinema_movie_ids if r.cinema_id == cinema.id]
            cinema_dict = \
                {
                    'id': cinema.id,
                    'location': {
                        'address':
                            {
                                'ru': cinema.address,
                                'en': cinema.address_en
                            },
                        'metro':
                            {
                                'ru': cinema.metro.split(', ') if cinema.metro else None,
                                'en': cinema.metro_en.split(', ') if cinema.metro_en else None
                            },
                        'latitude': float(cinema.latitude) if cinema.latitude else None,
                        'longitude': float(cinema.longitude) if cinema.longitude else None
                    },
                    'name': {
                        'ru': cinema.name,
                        'en': cinema.name_en
                    },
                    'phones': cinema.phone.split(', ') if cinema.phone else None,
                    'urls': cinema.url.split(', ') if cinema.url else None,
                    'movies': movie_ids,
                    'movies_count': len(movie_ids)
                }
            result.append(cinema_dict)
        return result
