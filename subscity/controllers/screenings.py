import datetime
from typing import List

from subscity.models.screening import Screening
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap


class ScreeningsController(object):
    @classmethod
    def get_for_cinema(cls, cinema_id: int, city: str) -> List:
        rows = Screening.get_for_cinema(cinema_id, city)
        return cls.render_screenings(rows)

    @classmethod
    def get_for_day(cls, date: datetime, city: str) -> List:
        rows = Screening.get_for_day(date, city)
        return cls.render_screenings(rows)

    @classmethod
    def render_screenings(cls, rows):
        result = []
        for row in rows:
            screening_dict = {'movie_id': row.Movie.id,
                              'cinema_id': row.Cinema.id,
                              'cinema_name': row.Cinema.name,
                              'date_time': row.Screening.date_time.isoformat(),
                              'tickets_url': Yap.url_tickets(row.Cinema.api_id, row.Screening.city,
                                                             row.Screening.day),
                              'id': row.Screening.id,
                              'movie_title': row.Movie.title,
                              'price': row.Screening.price_min}
            result.append(screening_dict)

        result = sorted(result, key=lambda k: (k['movie_title'], k['cinema_name']))
        return result
