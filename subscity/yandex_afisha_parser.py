# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import List, Dict, Optional

import xmltodict

from subscity.utils import read_file


class YandexAfishaParser:
    LOCAL_BASE_STORAGE = '/tmp/subscity_afisha_files'
    # CITIES = ('msk', 'spb')
    BASE_URL = 'https://afisha.yandex.ru'
    HAS_SUBS_TAG = 'На языке оригинала, с русскими субтитрами'
    DAY_STARTS_AT = timedelta(hours=2.5)  # day starts @ 02:30 and not 00:00
    MIN_DAYS_BEFORE_FIRST_SCREENING = 5
    CITIES_MAPPING = {'msk': 2, 'spb': 3}  # legacy: values for compatibility with v2

    @classmethod
    def url_tickets(cls, cinema_api_id: str, city: str, day: datetime) -> str:
        return '{}/places/{}?city={}&place-schedule-date={}'.\
            format(cls.BASE_URL, cinema_api_id, city, day.strftime("%Y-%m-%d"))

    @classmethod
    def get_movies(cls, city_abbr: str) -> List[Dict]:
        result = []
        file = '{}/afisha_files/{}/cinema/events.xml'.format(cls.LOCAL_BASE_STORAGE, city_abbr)
        parsed = xmltodict.parse(read_file(file))
        for item in parsed['events']['event']:
            result.append({
                'api_id': item['e'],
                'cast': cls._get_cast(item),
                'countries': item.get('ct'),
                'description': item.get('description'),
                'director': cls._get_directors(item),
                'duration': cls._get_duration(item),
                'genres': cls._get_genres(item),
                'kinopoisk_id': cls._get_kinopoisk_id(item),
                'poster_url': item.get('cover'),
                'premiere': cls._get_premiere(item),
                'title': item.get('t'),
                'title_original': item.get('or'),
                'year': cls._get_year(item)
            })
        return result

    @staticmethod
    def _get_cast(item: dict) -> Optional[str]:
        directors = item.get('cast')
        if not directors:
            return None
        return ', '.join(directors.split(', ')[:10])

    @staticmethod
    def _get_directors(item: dict) -> Optional[str]:
        directors = item.get('d')
        if not directors:
            return None
        return ', '.join(directors.split(', ')[:5])

    @staticmethod
    def _get_duration(item: dict) -> Optional[int]:
        duration = item.get('du', [None])[0]
        if not duration:
            return None
        return int(duration)

    @staticmethod
    def _get_year(item: dict) -> Optional[int]:
        year = item.get('y')
        if not year:
            return None
        return int(year)

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
        return datetime.strptime(date, '%Y-%m-%d')

    @staticmethod
    def _get_screening_time(item: dict) -> Optional[datetime]:
        date = item['@time']
        return datetime.strptime(date, '%Y-%m-%dT%H:%M')

    @staticmethod
    def _get_screening_price(item: dict) -> Optional[float]:
        price = item.get('@min_price')
        if not price:
            return None
        return int(float(price) / 100)

    @classmethod
    def _is_screening_with_subs(cls, item: dict) -> bool:
        return item.get('@language_notes') == cls.HAS_SUBS_TAG

    @classmethod
    def get_screenings(cls, city: str) -> List[Dict]:
        result = []
        file = '{base}/afisha_files/{city}/cinema/bilet.xml'.format(base=cls.LOCAL_BASE_STORAGE,
                                                                    city=city)
        parsed = xmltodict.parse(read_file(file), force_list=('cinema', 'event', 'show'))
        for cinema in parsed['tickets']['cinema']:
            for movie in cinema['event']:
                for screening in movie['show']:
                    if cls._is_screening_with_subs(screening):
                        result.append({
                            'cinema_api_id': cinema['@id'],
                            'movie_api_id': movie['@id'],
                            'ticket_api_id': screening.get('@bilet_id'),
                            'city': city,
                            'price_min': cls._get_screening_price(screening),
                            'price_max': cls._get_screening_price(screening),
                            'date_time': cls._get_screening_time(screening),
                            'source': 'yandex'})
        return result

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
                           'city_id': cls.CITIES_MAPPING[city_abbr],
                           'latitude': float(item['lat']),
                           'longitude': float(item['lon'])})
        return result
