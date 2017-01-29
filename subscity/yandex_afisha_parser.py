from datetime import datetime, timedelta
from typing import List, Dict, Union
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

    @classmethod
    def url_movie(cls, api_id: str, city: str='moscow') -> str:
        url = cls.BASE_URL_API
        url += 'events/{}?city={}'.format(api_id, city)
        return url

    @classmethod
    def url_movies(cls, limit: int, offset: int, city: str) -> str:
        url = cls.BASE_URL_API
        url += 'events/actual?limit={}&offset={}&tag=cinema&hasMixed=0&city={}'. \
            format(limit, offset, city)
        return url

    @classmethod
    def url_cinemas(cls, limit: int, offset: int, city: str) -> str:
        url = cls.BASE_URL_API
        url += 'events/cinema/places?limit={}&offset={}&city={}'.format(limit, offset, city)
        return url

    @classmethod
    def url_cinema_schedule(cls, api_id: str, date: datetime, city: str) -> str:
        url = cls.BASE_URL_API
        date = date.strftime("%Y-%m-%d")
        url += 'places/{}/schedule_cinema?date={}&city={}'.format(api_id, date, city)
        return url

    @classmethod
    def get_movie_ids(cls, city: str) -> List[str]:
        offset = 0
        limit = 12
        total = limit
        result = []
        while offset < total:
            url = cls.url_movies(limit=limit, offset=offset, city=city)
            contents = cls.fetch(url)
            data = json.loads(contents)
            total = data['paging']['total']
            for data in data['data']:
                result.append(data['event']['id'])
            offset += limit
        return result

    @classmethod
    def get_movie(cls, api_id: str, city: str='moscow') -> Dict:
        url = cls.url_movie(api_id, city)
        content = cls.fetch(url)
        data = json.loads(content)
        movie = data['event']['data']

        return {
            'title': {'russian': movie['title'],
                      'original': movie['originalTitle']},
            'genres': cls._get_genres(movie['tags']),
            'countries': cls._get_countries(movie['countries']),
            'cast': cls._get_actors(movie['persons']),
            'director': cls._get_directors(movie['persons']),
            'year': movie['year'],
            'duration': movie['duration'],
            'age_restriction': cls._get_age_restriction(movie['contentRating']),
            'premiere': cls._get_premiere(movie['dateReleased']),
            'kinopoisk': cls._get_kinopoisk_data(movie['kinopoisk'])
        }

    @staticmethod
    def _get_original_genre(code: str) -> str:
        map_code_genre = {'musical_film': 'musical'}
        name = code
        if code in map_code_genre:
            name = map_code_genre[code]
        return name.capitalize()

    @classmethod
    def _get_genres(cls, tags: Union[List]) -> Dict:
        names = [t['name'] for t in (tags or []) if t['type'] == 'genre']
        codes = [cls._get_original_genre(t['code']) for t in (tags or []) if t['type'] == 'genre']

        return {'russian': ', '.join(names) or None,
                'original': ', '.join(codes) or None}

    @staticmethod
    def _get_kinopoisk_data(data: Union[Dict]) -> Dict:
        if not data:
            return {'id': None, 'rating': None, 'votes': None}
        id_ = int(data['url'].replace('http://kinopoisk.ru/film/', ''))
        rating = data['value']
        votes = data['votes']
        return {'id': id_, 'rating': rating, 'votes': votes}

    @staticmethod
    def _get_actors(data: Union[List]) -> Union[str]:
        actors = []
        for item in data or []:
            if item['role'] == 'actor':
                actors.extend(item['names'])
        actors = ', '.join(actors) or None
        return actors

    @staticmethod
    def _get_directors(data: Union[List]) -> Union[str]:
        directors = []
        for item in data or []:
            if item['role'] == 'director':
                directors.extend(item['names'])
        return', '.join(directors) or None

    @staticmethod
    def _get_premiere(date: Union[str]) -> Union[str]:
        if not date:
            return None
        return datetime.strptime(date, '%Y-%m-%d')

    @staticmethod
    def _get_countries(countries: Union[List]) -> Union[str]:
        if not countries:
            return None
        return ', '.join(countries)

    @staticmethod
    def _get_age_restriction(rating: Union[str]) -> Union[int]:
        if not rating:
            return None
        return int(rating.replace('+', ''))

    @classmethod
    def get_cinema_screenings(cls, api_id: str, date: datetime, city: str) -> List[Dict]:
        url = cls.url_cinema_schedule(api_id, date, city)
        contents = cls.fetch(url)
        data = json.loads(contents)
        movies = data['schedule']['items']
        result = []
        for movie in movies:
            tag_codes = set([x['code'].lower() for x in movie['event']['tags']])
            if cls.SKIPPED_GENRES.intersection(tag_codes):
                continue
            for schedule in movie['schedule']:
                if cls.HAS_SUBS_TAG.lower() \
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

    @classmethod
    def get_cinemas(cls, city: str) -> List[Dict]:
        result = []
        offset = 0
        limit = 20
        total = limit

        while offset < total:
            url = cls.url_cinemas(limit=limit, offset=offset, city=city)
            contents = cls.fetch(url)
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
