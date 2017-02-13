SubsCity JSON API
===================

All call results are cached for up to 15 minutes.

* [Movies List](#movies-list)
* [Movie Screenings List](#movie-screenings-list)
* [Cinemas List](#cinemas-list)
* [Cinema Screenings List](#cinema-screenings-list)
* [Date Screenings List](#date-screenings-list)

## Movies List

```
GET /movies/msk
GET /movies/spb
```

```JSON
[
    {
        "age_restriction": 16,
        "cast": {
            "en": ["Ryan Gosling, Emma Stone, J.K. Simmons"],
            "ru": ["Райан Гослинг", "Эмма Стоун", "Дж.К. Симмонс"]
        },
        "countries": {
            "en": ["USA"],
            "ru": ["США"]
        },
        "description": {
            "en": "A jazz pianist falls for an aspiring actress in Los Angeles.",
            "ru": null
        },
        "directors": {
            "en": ["Damien Chazelle"],
            "ru": ["Дэмьен Шазелл"]
        },
        "duration": 128,
        "genres": {
            "en": ["Musical", "Drama", "Romance", "Comedy"],
            "ru": ["музыкальный", "драма", "мелодрама", "комедия"]
        },
        "id": 19,
        "languages": {
            "en": null,
            "ru": null
        },
        "premiere": "2017-01-12",
        "ratings": {
            "imdb": {
                "id": 3783958,
                "rating": 8.5,
                "votes": 157270
            },
            "kinopoisk": {
                "id": 841081,
                "rating": 8.4,
                "votes": 54592
            }
        },
        "screenings": {
            "count": 40,
            "next": "2017-02-13T11:25:00"
        },
        "title": {
            "en": "La La Land",
            "ru": "Ла-Ла Ленд"
        },
        "year": 2016
    },

    ...

]
```

## Movie Screenings List

```
GET /screenings/msk/movie/<movie_id>
GET /screenings/spb/movie/<movie_id>
```

Example:

```JSON
[
  {
    "cinema_id": 1,
    "cinema_name": "Пять звёзд на Новокузнецкой",
    "date_time": "2017-02-14T11:20:00",
    "id": 110,
    "movie_id": 74,
    "movie_title": "Под покровом ночи",
    "price": 100.0,
    "tickets_url": "https://afisha.yandex.ru/places/554c5ecb179b116662abdb03?city=moscow&place-schedule-date=2017-02-14"
  },

  ...

]
```

## Cinemas List

```
GET /cinemas/msk
GET /cinemas/spb
```

Example:

```JSON
[
  {
    "id": 1,
    "location": {
        "address": {
            "ru": "Б. Овчинниковский пер., 16",
            "en": "B. Ovchinnikovskij per., 16"
        },
        "latitude": 55.744724,
        "longitude": 37.629882,
        "metro": {
            "ru": ["Новокузнецкая", "Третьяковская"],
            "en": ["Novokuznetskaja", "Tretjakovskaja"]
        }
    },
    "movies": [
        74,
        50,
        19,
        11,
        28,
        23
    ],
    "movies_count": 6,
    "name": {
        "ru": "Пять звёзд на Новокузнецкой",
        "en": "Pjat' zvezd na Novokuznetskoj"
    },
    "phones": [
        "+7 (495) 916-91-69 (заказ билетов)"
    ],
    "urls": [
        "http://www.5zvezd.ru"
    ]
  },

  ...

]
```

## Cinema Screenings List

```
GET /screenings/msk/cinema/<cinema_id>
GET /screenings/spb/cinema/<cinema_id>
```

Example:

```JSON
[
  {
    "cinema_id": 1,
    "cinema_name": "Пять звёзд на Новокузнецкой",
    "date_time": "2017-02-14T11:20:00",
    "id": 110,
    "movie_id": 74,
    "movie_title": "Под покровом ночи",
    "price": 100.0,
    "tickets_url": "https://afisha.yandex.ru/places/554c5ecb179b116662abdb03?city=moscow&place-schedule-date=2017-02-14"
  },

  ...

]
```

## Date Screenings List

```
GET /screenings/msk/date/<YYYY-MM-DD>
GET /screenings/spb/date/<YYYY-MM-DD>
```

Example:

```JSON
[
  {
    "cinema_id": 1,
    "cinema_name": "Пять звёзд на Новокузнецкой",
    "date_time": "2017-02-14T11:20:00",
    "id": 110,
    "movie_id": 74,
    "movie_title": "Под покровом ночи",
    "price": 100.0,
    "tickets_url": "https://afisha.yandex.ru/places/554c5ecb179b116662abdb03?city=moscow&place-schedule-date=2017-02-14"
  },

  ...

]
```

**NB**: Screenings belong to the day if they start between 02:31 AM of this day and 02:30 AM of the following one.