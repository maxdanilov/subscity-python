import json

from subscity.models.cinema import Cinema
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap


def update_database() -> None:
    for city in Yap.CITIES:
        cinemas = Yap.get_cinemas(city)
        for cinema in cinemas:
            cinema_obj = Cinema(**cinema)
            cinema_obj.save_or_update()


def update_test_fixtures() -> None:
    city = 'saint-petersburg'
    fixture_path = 'tests/fixtures/cinemas/{}/'.format(city)
    limit = 20
    for offset in [0, 20, 40, 60]:
        url = Yap.url_cinemas(limit=limit, offset=offset, city=city)
        filename = fixture_path + 'cinemas-offset{:02d}-limit{:02d}.json'.format(offset, limit)
        print("Downloading {} to {}".format(url, filename))
        parsed = json.loads(Yap.fetch(url))
        with open(filename, "w") as fp:
            fp.write(json.dumps(parsed, indent=4))
