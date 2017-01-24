import datetime
import json
import time

from subscity.models.cinema import Cinema
from subscity.models.screening import Screening
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap


def update_screenings() -> None:
    cinemas = Cinema.get_all()
    start_date = datetime.datetime.now()
    cleaned_count = Screening.clean(end_day=start_date)
    print("Cleaned {} screenings".format(cleaned_count))
    print("> Found {} cinemas in the database".format(len(cinemas)))
    for index, cinema in enumerate(cinemas):
        for date in (start_date + datetime.timedelta(days=n) for n in range(Yap.FETCH_DAYS)):
            print(">> [{}]/[{}] Fetching screenings @ {} for {}".format(index + 1, len(cinemas),
                                                                        date.strftime("%d.%m.%Y"),
                                                                        cinema.name))
            new_screenings_dicts = Yap.get_cinema_screenings(cinema.api_id, date, cinema.city)
            deleted_screenings = Screening.clean(cinema_api_id=cinema.api_id, start_day=date,
                                                 end_day=date + datetime.timedelta(days=1))
            print("+{} -{} screenings".format(len(new_screenings_dicts), deleted_screenings))

            for screening_dict in new_screenings_dicts:
                screening = Screening(**screening_dict)
                screening.save()
            time.sleep(1.5)


def update_cinemas() -> None:
    for city in Yap.CITIES:
        cinemas = Yap.get_cinemas(city)
        for cinema in cinemas:
            cinema_obj = Cinema(**cinema)
            cinema_obj.save_or_update()
        time.sleep(2)


def update_test_fixtures() -> None:
    update_test_cinema_fixtures()
    update_test_movie_fixtures()


def update_test_cinema_fixtures() -> None:
    city = 'saint-petersburg'
    fixture_path = 'tests/fixtures/cinemas/{}/'.format(city)
    limit = 20
    total_count = 70
    for offset in range(0, total_count, limit):
        url = Yap.url_cinemas(limit=limit, offset=offset, city=city)
        filename = fixture_path + 'cinemas-offset{:02d}-limit{:02d}.json'.format(offset, limit)
        print("Downloading {} to {}".format(url, filename))
        parsed = json.loads(Yap.fetch(url))
        with open(filename, "w") as fp:
            fp.write(json.dumps(parsed, indent=4))


def update_test_movie_fixtures() -> None:
    city = 'saint-petersburg'
    fixture_path = 'tests/fixtures/movies/{}/'.format(city)
    limit = 12
    total_count = 140
    for offset in range(0, total_count, limit):
        url = Yap.url_movies(limit=limit, offset=offset, city=city)
        filename = fixture_path + 'movies-offset{:03d}-limit{:02d}.json'.format(offset, limit)
        print("Downloading {} to {}".format(url, filename))
        parsed = json.loads(Yap.fetch(url))
        with open(filename, "w") as fp:
            fp.write(json.dumps(parsed, indent=4))
