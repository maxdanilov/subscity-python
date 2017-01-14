from datetime import datetime
from typing import List, Dict
import json
import urllib.request


class YandexAfishaParser(object):
    CITIES = ('moscow', 'saint-petersburg')
    BASE_URL_API = 'https://afisha.yandex.ru/api/'

    @staticmethod
    def fetch(url: str) -> str:
        print(url)
        return urllib.request.urlopen(url).read()

    @staticmethod
    def url_movies(limit: int, offset: int, city: str) -> str:
        url = YandexAfishaParser.BASE_URL_API
        url += 'events/actual?limit={}&offset={}&tag=cinema&hasMixed=0&city={}'. \
            format(limit, offset, city)
        return url

    @staticmethod
    def url_cinemas(limit: int, offset: int, city: str) -> str:
        url = YandexAfishaParser.BASE_URL_API
        url += 'events/cinema/places?limit={}&offset={}&city={}'.format(limit, offset, city)
        return url

    @staticmethod
    def url_cinema_schedule(api_id: str, date: datetime, city: str) -> str:
        url = YandexAfishaParser.BASE_URL_API
        date = date.strftime("%Y-%m-%d")
        url += 'places/{}/schedule_cinema?date={}&city={}'.format(api_id, date, city)
        return url

    @staticmethod
    def get_cinemas(city: str) -> List[Dict]:
        result = []
        offset = 0
        limit = 20
        total = limit

        while offset < total:
            url = YandexAfishaParser.url_cinemas(limit=limit, offset=offset, city=city)
            contents = YandexAfishaParser.fetch(url)
            data = json.loads(contents)
            total = data['paging']['total']
            for data in data['items']:
                metro = ', '.join([station['name'] for station in data['metro']])
                result.append({'api_id': data['id'],
                               'name': data['title'],
                               'address': data['address'],
                               'phone': ', '.join(sum([x['numbers'] for x in data['phones']], [])),
                               'url': ', '.join(data['links']),
                               'metro': metro,
                               'city': city,
                               'latitude': data['coordinates']['latitude'],
                               'longitude': data['coordinates']['longitude']})
            offset += limit
        return result


# if __name__ == '__main__':
#     CINEMAS = YandexAfishaParser.get_cinemas('moscow')
#     CINEMAS = YandexAfishaParser.get_cinemas('saint-petersburg')
