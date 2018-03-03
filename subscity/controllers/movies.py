from collections import namedtuple
from typing import List

from subscity.models.movie import Movie
from subscity.models.screening import Screening


class MoviesController(object):
    @classmethod
    def get_movies(cls, city: str) -> List:
        movies_api_ids_stats = Screening.get_movie_api_ids(city)
        movies_api_ids = [r.movie_api_id for r in movies_api_ids_stats]
        movies = Movie.get_by_api_ids(movies_api_ids)
        return cls.render_movies(movies, movies_api_ids_stats)

    @classmethod
    def get_movie(cls, city: str, movie_id: int) -> dict:
        movies_api_ids_stats = Screening.get_movie_api_ids(city)
        movie = Movie.get_by_id(movie_id)

        if not movie:
            return {}
        stats = next((obj for obj in movies_api_ids_stats if obj.movie_api_id == movie.api_id),
                     None)
        return cls.render_movie(movie, stats)

    @classmethod
    def render_movies(cls, movies: List, movies_api_ids_stats: List) -> List:
        result = []
        for movie in movies:
            if movie.hide:
                continue
            stats = next((obj for obj in movies_api_ids_stats if obj.movie_api_id == movie.api_id),
                         None)
            if not stats:
                continue
            result.append(cls.render_movie(movie, stats))
        return result

    @classmethod
    def render_movie(cls, movie: Movie, stats: namedtuple) -> dict:
        # TODO poster, trailers

        stats_info = {
            'screenings': stats.screenings if stats else 0,
            'cinemas': stats.cinemas if stats else 0,
            'next_screening': stats.next_screening.isoformat() if stats else None
        }

        return {
            'id': movie.id,
            'age_restriction': movie.age_restriction,
            'duration': movie.duration,
            'year': movie.year,
            'cast':
                {
                    'en': movie.cast_en.split(', ') if movie.cast_en else None,
                    'ru': movie.cast.split(', ') if movie.cast else None
                },
            'genres':
                {
                    'en': movie.genres_en.split(', ') if movie.genres_en else None,
                    'ru': movie.genres.split(', ') if movie.genres else None,
                },
            'directors':
                {
                    'en': movie.directors_en.split(', ') if movie.directors_en else None,
                    'ru': movie.directors.split(', ') if movie.directors else None,
                },
            'countries':
                {
                    'en': movie.countries_en.split(', ') if movie.countries_en else None,
                    'ru': movie.countries.split(', ') if movie.countries else None
                },
            'description':
                {
                    'en': movie.description_en,
                    'ru': movie.description,
                },
            'languages':
                {
                    'en': movie.languages_en.split(', ') if movie.languages_en else None,
                    'ru': movie.languages.split(', ') if movie.languages else None,
                },
            'title':
                {
                    'en': movie.title_en,
                    'ru': movie.title
                },
            'stats': stats_info,
            'ratings':
                {
                    'kinopoisk':
                        {
                            'id': movie.kinopoisk_id,
                            'rating': movie.kinopoisk_rating,
                            'votes': movie.kinopoisk_votes
                        },
                    'imdb':
                        {
                            'id': movie.imdb_id,
                            'rating': movie.imdb_rating,
                            'votes': movie.imdb_votes
                        }
                },
            'premiere': movie.premiere.strftime("%Y-%m-%d") if movie.premiere else None
        }
