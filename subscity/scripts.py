import os
import shutil
import sys
import tarfile
import traceback
import urllib

import requests

from subscity.main import DB
from subscity.models.cinema import Cinema
from subscity.models.movie import Movie
from subscity.models.screening import Screening
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap


def update_screenings() -> None:
    for city in Yap.CITIES_MAPPING:
        screenings = Yap.get_screenings(city)
        print(f'{city} Parsed new screenings: {len(screenings)}')

        screenings_all = [Screening(**screening_dict) for screening_dict in screenings]
        screenings_to_save = Screening.filter_invalid(screenings_all)
        screenings_to_skip = [s for s in screenings_all if s not in screenings_to_save]

        count = Screening.clean(city=city)
        print(f'{city} Dropped screenings: {count}')

        count = Screening.bulk_save(screenings_to_save)
        print(f'{city} Saved screenings: {count}')
        print(f'{city} Skipped screenings to keep DB integrity: {len(screenings_to_skip)}')

        count = Screening.clean_hidden(city=city)
        print(f'{city} Dropped screening for hidden movies: {count}')

        count = Screening.clean_premature(city=city)
        print(f'{city} Dropped premature screenings: {count}')


def update_cinemas() -> None:
    for city in Yap.CITIES_MAPPING:
        cinemas = Yap.get_cinemas(city)
        for cinema in cinemas:
            try:
                print("{} Updating cinema {} ({})".format(city, cinema['name'], cinema['api_id']))
                cinema_obj = Cinema(**cinema)
                cinema_obj.create_or_update()
            except Exception:  # pylint:disable=broad-except
                traceback.print_exc()
                DB.session.rollback()


def update_movies() -> None:
    for city in Yap.CITIES_MAPPING:
        movies = Yap.get_movies(city)
        movie_api_ids = [m['api_id'] for m in movies]
        movie_api_ids_db = Movie.get_all_api_ids()
        new_api_ids = [i for i in movie_api_ids if i not in movie_api_ids_db]
        new_movies = [m for m in movies if m['api_id'] in new_api_ids]
        for movie in new_movies:
            try:
                print("Saving movie {} ({})".format(movie['title'], movie['api_id']))
                Movie(**movie).save()
            except Exception:  # pylint:disable=broad-except
                traceback.print_exc()
                DB.session.rollback()


def update_test_fixtures() -> None:
    update_test_cinema_fixtures()
    update_test_movie_fixtures()
    update_test_screening_fixtures()


def _update_test_fixture(city: str, entity: str, fixture_name: str) -> None:
    fixture_path = 'tests/fixtures/{}/{}/'.format(entity, city)
    shutil.copy2('{}/afisha_files/{}/cinema/{}'.format(Yap.LOCAL_BASE_STORAGE, city, fixture_name),
                 fixture_path + fixture_name)


def update_test_cinema_fixtures() -> None:
    _update_test_fixture('spb', 'cinemas', 'places.xml')


def update_test_movie_fixtures() -> None:
    _update_test_fixture('spb', 'movies', 'events.xml')


def update_test_screening_fixtures() -> None:
    _update_test_fixture('spb', 'screenings', 'bilet.xml')


# TODO test me
def update_base() -> None:
    base_download_url = 'https://afisha.yandex.ru/export/legacy'
    auth_token = os.environ.get('YANDEX_AUTH_TOKEN')
    headers = {'Authorization': 'token {0}'.format(auth_token)}
    req = requests.get(base_download_url, headers=headers)
    if req.status_code != 200:
        print('Error code during API call: {}'.format(req.status_code))
        sys.exit(1)

    url = req.json()[0]['url']
    print('Downloading {}'.format(url))
    file_name = "archive.tar.gz"
    urllib.request.urlretrieve(url, file_name)

    print('Cleaning old data')
    shutil.rmtree(Yap.LOCAL_BASE_STORAGE, ignore_errors=True)

    print('Extracting archive')
    tar = tarfile.open(file_name, 'r:gz')
    tar.extractall(Yap.LOCAL_BASE_STORAGE)
    tar.close()

    print("Reformatting with xmllint")
    os.system("find " + Yap.LOCAL_BASE_STORAGE + " -path \"*cinema/*.xml\" -type f -exec "
                                                 "xmllint --output '{}' --format '{}' \\;")

    print('Removing archive')
    os.remove(file_name)
