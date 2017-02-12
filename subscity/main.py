# -*- coding: utf-8 -*-
import os

from flask_sqlalchemy import SQLAlchemy
from voluptuous import Schema, Required, MultipleInvalid, All, Range, Coerce

from subscity.app import get_app
from subscity.controllers.screenings import ScreeningsController
from subscity.utils import validator_date, validator_city, json_response, error_msg

DB_URI = os.environ.get('DB_URI')

APP = get_app()
DB = SQLAlchemy(APP)


@APP.route('/screenings/<city>/movie/<movie_id>')
def get_screenings_for_movie(city: str, movie_id: str) -> (str, int):
    validator = Schema({Required('id'): All(Coerce(int), Range(min=1),
                                            msg='movie id must be an integer'),
                        Required('city'): validator_city()})
    try:
        validated = validator({'id': movie_id, 'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = ScreeningsController.get_for_movie(validated['id'], validated['city'])
    return json_response(result), 200


@APP.route('/screenings/<city>/cinema/<cinema_id>')
def get_screenings_for_cinema(city: str, cinema_id: str) -> (str, int):
    validator = Schema({Required('id'): All(Coerce(int), Range(min=1),
                                            msg='cinema id must be an integer'),
                        Required('city'): validator_city()})
    try:
        validated = validator({'id': cinema_id, 'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = ScreeningsController.get_for_cinema(validated['id'], validated['city'])
    return json_response(result), 200


@APP.route('/screenings/<city>/date/<date>')
def get_screenings_for_day(city: str, date: str) -> (str, int):
    validator = Schema({Required('date'): validator_date(),
                        Required('city'): validator_city()})
    try:
        validated = validator({'date': date, 'city': city})
    except MultipleInvalid as exc:
        return json_response(error_msg(exc)), 400
    result = ScreeningsController.get_for_day(validated['date'], validated['city'])
    return json_response(result), 200
