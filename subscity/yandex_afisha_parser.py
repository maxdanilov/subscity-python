# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import urllib.request

import xmltodict

from subscity.utils import read_file


class YandexAfishaParser(object):
    LOCAL_BASE_STORAGE = '/tmp/subscity_afisha_files'
    CITIES = ('moscow', 'saint-petersburg')
    CITIES_ABBR = ('msk', 'spb')
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
    def url_cinema_schedule(cls, api_id: str, date: datetime, city: str) -> str:
        url = cls.BASE_URL_API
        date = date.strftime("%Y-%m-%d")
        url += 'places/{}/schedule_cinema?date={}&city={}'.format(api_id, date, city)
        return url

    @classmethod
    def get_movies(cls, city_abbr: str) -> List[Dict]:
        result = []
        file = '{}/afisha_files/{}/cinema/events.xml'.format(cls.LOCAL_BASE_STORAGE, city_abbr)
        parsed = xmltodict.parse(read_file(file))
        for item in parsed['events']['event']:
            result.append({
                'api_id': item['e'],
                'cast': item.get('cast'),
                'countries': item.get('ct'),
                'description': item.get('description'),
                'directors': item.get('d'),
                'duration': cls._get_duration(item),
                'genres': cls._get_genres(item),
                'kinopoisk_id': cls._get_kinopoisk_id(item),
                'poster_url': item.get('cover'),
                'premiere': cls._get_premiere(item),
                'title': item.get('t'),
                'title_en': item.get('or'),
                'year': cls._get_year(item)
            })
        return result

    # TODO test me
    @staticmethod
    def _get_duration(item: dict) -> Optional[int]:
        duration = item.get('du', [None])[0]
        if not duration:
            return None
        return int(duration)

    # TODO test me
    @staticmethod
    def _get_year(item: dict) -> Optional[int]:
        year = item.get('y')
        if not year:
            return None
        return int(year)

    # TODO test me
    @staticmethod
    def _get_kinopoisk_id(item: dict) -> Optional[int]:
        kp_id = item.get('coid', [None])
        if not isinstance(kp_id, list):
            kp_id = [kp_id]
        if kp_id == [None]:
            return None
        return int(kp_id[0])

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
    def _get_genres(cls, item: dict) -> Optional[str]:
        genres_str = item.get('g')
        if not genres_str:
            return None
        genres = genres_str.split(', ')
        return ', '.join([cls._get_genre(g) for g in genres])

    @staticmethod
    def _get_premiere(item: dict) -> Optional[datetime]:
        date = item.get('release_date')
        if not date:
            return None
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    # TODO replace me
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

    # TODO test me
    @staticmethod
    def _get_metro(item: dict) -> Optional[str]:
        metro_stations = item.get('mm', {}).get('s', [])
        if not isinstance(metro_stations, list):
            metro_stations = [metro_stations]
        metro = ', '.join([x['#text'] for x in metro_stations])
        metro = metro if metro else None
        return metro

    @classmethod
    def get_cinemas(cls, city_abbr: str) -> List[Dict]:
        result = []
        file = '{}/afisha_files/{}/cinema/places.xml'.format(cls.LOCAL_BASE_STORAGE, city_abbr)
        parsed = xmltodict.parse(read_file(file))
        for item in parsed['places']['place']:
            result.append({'api_id': item['p'],
                           'name': item['t'],
                           'address': item.get('a'),
                           'phone': item.get('is'),
                           'url': item.get('w'),
                           'metro': cls._get_metro(item),
                           'city': city_abbr,
                           'latitude': float(item['lat']),
                           'longitude': float(item['lon'])})
        return result
