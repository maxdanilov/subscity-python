from datetime import datetime, timedelta
from typing import List, Dict
import json
import urllib.request


class YandexAfishaParser(object):
    CITIES = ('moscow', 'saint-petersburg')
    BASE_URL_API = 'https://afisha.yandex.ru/api/'
    SKIPPED_GENRES = set([x.lower() for x in ['TheatreHD']])
    HAS_SUBS_TAG = 'На языке оригинала'
    DAY_STARTS_AT = timedelta(hours=2.5)  # day starts @ 02:30 and not 00:00
    FETCH_DAYS = 2

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
    def get_movie_ids(city: str) -> List[str]:
        offset = 0
        limit = 12
        total = limit
        result = []
        while offset < total:
            url = YandexAfishaParser.url_movies(limit=limit, offset=offset, city=city)
            contents = YandexAfishaParser.fetch(url)
            data = json.loads(contents)
            total = data['paging']['total']
            for data in data['data']:
                result.append(data['event']['id'])
            offset += limit
        return result

    @staticmethod
    def get_cinema_screenings(api_id: str, date: datetime, city: str) -> List[Dict]:
        url = YandexAfishaParser.url_cinema_schedule(api_id, date, city)
        contents = YandexAfishaParser.fetch(url)
        data = json.loads(contents)
        movies = data['schedule']['items']
        result = []
        for movie in movies:
            tag_codes = set([x['code'].lower() for x in movie['event']['tags']])
            if YandexAfishaParser.SKIPPED_GENRES.intersection(tag_codes):
                continue
            for schedule in movie['schedule']:
                if YandexAfishaParser.HAS_SUBS_TAG.lower() \
                        in [x['name'].lower() for x in schedule['tags']]:
                    for session in schedule['sessions']:
                        min_price = max_price = ticket_id = None
                        if session['ticket']:
                            ticket_id = session['ticket']['id']
                            min_price = (session['ticket']['price']['min'] or 0) / 100 or None
                            max_price = (session['ticket']['price']['max'] or 0) / 100 or None
                        screening = {
                            'cinema_api_id': api_id,
                            'movie_api_id': movie['event']['id'],
                            'ticket_api_id': ticket_id,
                            'date_time': session['datetime'],
                            'city': city,
                            'price_min': min_price,
                            'price_max': max_price}
                        result.append(screening)
        return result

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
