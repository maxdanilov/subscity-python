# -*- coding: utf-8 -*-

import os

from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from voluptuous import Schema, Required, MultipleInvalid, All, Range, Coerce

from subscity.app import get_app
from subscity.controllers.screenings import ScreeningsController
from subscity.utils import validator_date, validator_city

DB_URI = os.environ.get('DB_URI')

APP = get_app()
DB = SQLAlchemy(APP)


@APP.route('/')
def hello_world() -> str:
    return u'SubsCity API'


@APP.route('/screenings/<city_code>/cinema/<cinema_id_str>')
def get_screenings_for_cinema(city_code: str, cinema_id_str: str) -> (str, int):
    validator = Schema({Required('id'): All(Coerce(int), Range(min=1),
                                            msg='cinema id must be an integer'),
                        Required('city'): validator_city()})
    try:
        validated = validator({'id': cinema_id_str, 'city': city_code})
        city = validated['city']
        cinema_id = validated['id']
    except MultipleInvalid as exc:
        return jsonify({'errors': [e.msg for e in exc.errors]}), 400
    result = ScreeningsController.get_for_cinema(cinema_id, city)
    return jsonify(result), 200


@APP.route('/screenings/<city_code>/date/<date_str>')
def get_screenings_for_day(city_code: str, date_str: str) -> (str, int):
    validator = Schema({Required('date'): validator_date(),
                        Required('city'): validator_city()})
    try:
        validated = validator({'date': date_str, 'city': city_code})
        city = validated['city']
        date = validated['date']
    except MultipleInvalid as exc:
        return jsonify({'errors': [e.msg for e in exc.errors]}), 400
    result = ScreeningsController.get_for_day(date, city)
    return jsonify(result), 200
