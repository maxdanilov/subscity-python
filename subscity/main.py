# -*- coding: utf-8 -*-
import os

from flask import Response, request
from flask_sqlalchemy import SQLAlchemy
from voluptuous import Schema, Required, MultipleInvalid, All, Range, Coerce, wraps

from subscity.app import get_app
from subscity.controllers.cinemas import CinemasController
from subscity.controllers.movies import MoviesController
from subscity.controllers.screenings import ScreeningsController
from subscity.models.account import Account
from subscity.utils import validator_date, validator_city, json_response, error_msg

DB_URI = os.environ.get('DB_URI')

APP = get_app()
DB = SQLAlchemy(APP)


def requires_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not Account.check(request.headers.get('Authorization')):
            return json_response({'result': 'not allowed'}), 403
        return func(*args, **kwargs)
    return decorated


@APP.route('/<city>/movies', methods=['GET'])
def get_movies(city: str) -> (Response, int):
    validator = Schema({Required('city'): validator_city()})
    try:
        validated = validator({'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = MoviesController.get_movies(validated['city'])
    return json_response(result), 200


@APP.route('/<city>/movies/<movie_id>', methods=['GET'])
def get_movie(city: str, movie_id: str) -> (Response, int):
    validator = Schema({Required('movie_id'): All(Coerce(int), Range(min=1),
                                                  msg='movie id must be an integer'),
                        Required('city'): validator_city()})
    try:
        validated = validator({'movie_id': movie_id, 'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = MoviesController.get_movie(validated['movie_id'])
    code = 200 if result else 404
    return json_response(result), code


@APP.route('/<city>/cinemas', methods=['GET'])
def get_cinemas(city: str) -> (Response, int):
    validator = Schema({Required('city'): validator_city()})
    try:
        validated = validator({'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = CinemasController.get_cinemas(validated['city'])
    return json_response(result), 200


@APP.route('/<city>/screenings/movie/<movie_id>', methods=['GET'])
def get_screenings_for_movie(city: str, movie_id: str) -> (Response, int):
    validator = Schema({Required('id'): All(Coerce(int), Range(min=1),
                                            msg='movie id must be an integer'),
                        Required('city'): validator_city()})
    try:
        validated = validator({'id': movie_id, 'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = ScreeningsController.get_for_movie(validated['id'], validated['city'])
    return json_response(result), 200


@APP.route('/<city>/screenings/cinema/<cinema_id>', methods=['GET'])
def get_screenings_for_cinema(city: str, cinema_id: str) -> (Response, int):
    validator = Schema({Required('id'): All(Coerce(int), Range(min=1),
                                            msg='cinema id must be an integer'),
                        Required('city'): validator_city()})
    try:
        validated = validator({'id': cinema_id, 'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = ScreeningsController.get_for_cinema(validated['id'], validated['city'])
    return json_response(result), 200


@APP.route('/<city>/screenings/date/<date>', methods=['GET'])
def get_screenings_for_day(city: str, date: str) -> (Response, int):
    validator = Schema({Required('date'): validator_date(),
                        Required('city'): validator_city()})
    try:
        validated = validator({'date': date, 'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = ScreeningsController.get_for_day(validated['date'], validated['city'])
    return json_response(result), 200


@APP.route('/secret')
@requires_auth
def get_info() -> (Response, int):
    return json_response({'result': 42}), 200
