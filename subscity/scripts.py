import datetime
import os
import shutil
import tarfile
import time
import traceback
import urllib

import requests

from subscity.main import DB
from subscity.models.cinema import Cinema
from subscity.models.movie import Movie
from subscity.models.screening import Screening
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap
from tests.utils import download_to_json


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
            try:
                update_screenings_cinema(cinema, date)
            except Exception:  # pylint:disable=broad-except
                traceback.print_exc()
                DB.session.rollback()
            time.sleep(1.5)


def update_screenings_cinema(cinema: Cinema, date: datetime) -> None:
    new_screenings_dicts = Yap.get_cinema_screenings(cinema.api_id, date, cinema.city)
    deleted_screenings = Screening.clean(cinema_api_id=cinema.api_id, start_day=date,
                                         end_day=date + datetime.timedelta(days=1))
    print("+{} -{} screenings".format(len(new_screenings_dicts), deleted_screenings))
    for screening_dict in new_screenings_dicts:
        screening = Screening(**screening_dict)
        screening.save()


def update_cinemas() -> None:
    for city in Yap.CITIES:
        cinemas = Yap.get_cinemas(city)
        for cinema in cinemas:
            cinema_obj = Cinema(**cinema)
            cinema_obj.create_or_update()
        time.sleep(2)


def update_movies() -> None:
    for city in Yap.CITIES:
        movie_api_ids = Yap.get_movie_ids(city)
        movie_api_ids_db = Movie.get_all_api_ids()
        new_api_ids = [i for i in movie_api_ids if i not in movie_api_ids_db]
        for index, api_id in enumerate(new_api_ids):
            print("{} / {} Fetching {}".format(index + 1, len(new_api_ids), api_id))
            try:
                movie = Yap.get_movie(api_id, city)
                Movie(**movie).save()
            except Exception:  # pylint:disable=broad-except
                traceback.print_exc()
                DB.session.rollback()
            time.sleep(1.5)


def update_test_fixtures() -> None:
    update_test_cinema_fixtures()
    update_test_movie_fixtures()
    update_test_movie_details_fixtures()


def update_test_cinema_fixtures() -> None:
    city = 'saint-petersburg'
    fixture_path = 'tests/fixtures/cinemas/{}/'.format(city)
    limit = 20
    total_count = 70
    for offset in range(0, total_count, limit):
        url = Yap.url_cinemas(limit=limit, offset=offset, city=city)
        filename = fixture_path + 'cinemas-offset{:02d}-limit{:02d}.json'.format(offset, limit)
        download_to_json(url, filename)


def update_test_movie_fixtures() -> None:
    city = 'saint-petersburg'
    fixture_path = 'tests/fixtures/movies/{}/'.format(city)
    limit = 12
    total_count = 140
    for offset in range(0, total_count, limit):
        url = Yap.url_movies(limit=limit, offset=offset, city=city)
        filename = fixture_path + 'movies-offset{:03d}-limit{:02d}.json'.format(offset, limit)
        download_to_json(url, filename)


def update_test_movie_details_fixtures() -> None:
    api_id = '5874ea2a685ae0b186614bb5'
    for city in Yap.CITIES:
        fixture_path = 'tests/fixtures/movies/{}/'.format(city)
        url = Yap.url_movie(api_id=api_id, city=city)
        filename = fixture_path + '{}.json'.format(api_id)
        download_to_json(url, filename)


def download_base() -> None:
    base_download_url = 'https://afisha.yandex.ru/export/legacy'
    auth_token = os.environ.get('YANDEX_AUTH_TOKEN')
    headers = {'Authorization': 'token {0}'.format(auth_token)}
    req = requests.get(base_download_url, headers=headers)
    if req.status_code != 200:
        print('Error code during API call: {}'.format(req.status_code))
        exit(1)

    url = req.json()['data'][0]['url']
    print('Downloading {}'.format(url))
    file_name = "archive.tar.gz"
    urllib.request.urlretrieve(url, file_name)

    print('Cleaning old data')
    shutil.rmtree(Yap.LOCAL_BASE_STORAGE, ignore_errors=True)

    print('Extracting archive')
    tar = tarfile.open(file_name, 'r:gz')
    tar.extractall(Yap.LOCAL_BASE_STORAGE)
    tar.close()

    print('Removing archive')
    os.remove(file_name)
