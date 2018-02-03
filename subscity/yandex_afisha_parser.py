# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import List, Dict, Union
import json
import re
import urllib.request

from subscity.utils import html_to_text


class YandexAfishaParser(object):
    LOCAL_BASE_STORAGE = '/tmp/subscity_afisha_files'
    CITIES = ('moscow', 'saint-petersburg')
    BASE_URL = 'https://afisha.yandex.ru'
    BASE_URL_API = '{}/api/'.format(BASE_URL)
    SKIPPED_GENRES = set([x.lower() for x in ['TheatreHD']])
    HAS_SUBS_TAG = 'На языке оригинала'
    DAY_STARTS_AT = timedelta(hours=2.5)  # day starts @ 02:30 and not 00:00
    FETCH_DAYS = 10

    @staticmethod
    def fetch(url: str) -> str:
        print(url)
        return urllib.request.urlopen(url).read().decode('utf-8')

    @classmethod
    def url_tickets(cls, cinema_api_id: str, city: str, day: datetime) -> str:
        return '{}/places/{}?city={}&place-schedule-date={}'.\
            format(cls.BASE_URL, cinema_api_id, city, day.strftime("%Y-%m-%d"))

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
                id_ = data['event']['id']
                if id_ not in result:
                    result.append(id_)
            offset += limit
        return result

    @classmethod
    def get_movie(cls, api_id: str, city: str='moscow') -> Dict:
        url = cls.url_movie(api_id, city)
        content = cls.fetch(url)
        data = json.loads(content)
        movie = data['event']['data']
        kinopoisk_data = cls._get_kinopoisk_data(movie['kinopoisk'])
        genres_data = cls._get_genres(movie['tags'])

        return {
            'api_id': movie.get('id'),
            'title': movie.get('title'),
            'title_en': movie.get('originalTitle'),
            'description': movie.get('description') or html_to_text(movie.get('descriptionHtml')),
            'genres': genres_data.get('russian'),
            'genres_en': genres_data.get('original'),
            'countries': cls._get_countries(movie.get('countries')),
            'cast': cls._get_actors(movie.get('persons')),
            'directors': cls._get_directors(movie.get('persons')),
            'year': movie.get('year'),
            'duration': movie.get('duration'),
            'age_restriction': cls._get_age_restriction(movie.get('contentRating')),
            'premiere': cls._get_premiere(movie.get('dateReleased')),
            'kinopoisk_id': kinopoisk_data['id'],
            'kinopoisk_votes': kinopoisk_data['votes'],
            'kinopoisk_rating': kinopoisk_data['rating']
        }

    @staticmethod
    def _get_original_genre(code: str) -> str:
        map_code_genre = {'musical_film': 'musical',
                          'art_film': 'indie',
                          'biographic': 'biography',
                          'family_movie': 'family',
                          'film_noir': 'noir',
                          'mysticism': 'mystery',
                          'short_film': 'short'}
        name = code
        if code in map_code_genre:
            name = map_code_genre[code]
        return name.title()

    @staticmethod
    def _get_genre(name: str) -> str:
        map_name_genre = {'авторское кино': 'артхаус',
                          'документальное кино': 'документальный',
                          'короткометражный фильм': 'короткометражный',
                          'музыка народов мира': 'музыкальный',
                          'семейное кино': 'семейный',
                          'фильм-нуар': 'нуар'}
        if name in map_name_genre:
            return map_name_genre[name]
        return name

    @classmethod
    def _get_genres(cls, tags: Union[List]) -> Dict:
        names = [cls._get_genre(t['name']) for t in (tags or []) if t['type'] == 'genre']
        codes = [cls._get_original_genre(t['code']) for t in (tags or []) if t['type'] == 'genre']

        return {'russian': ', '.join(names) or None,
                'original': ', '.join(codes) or None}

    @staticmethod
    def _get_kinopoisk_data(data: Union[Dict]) -> Dict:
        if not data:
            return {'id': None, 'rating': None, 'votes': None}
        id_ = int(re.sub(r'\D', '', data['url']))
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
        return ', '.join(directors) or None

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
        if not rating or rating.lower() == 'none':
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
