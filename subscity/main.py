# -*- coding: utf-8 -*-

import os

from flask_sqlalchemy import SQLAlchemy

from subscity.app import get_app
from subscity.models.screening import Screening

DB_URI = os.environ.get('DB_URI')

APP = get_app()
DB = SQLAlchemy(APP)


@APP.route('/')
def hello_world() -> str:
    return u'Hello, World! тест'


@APP.route('/screenings')
def get_screenings() -> str:
    screenings = Screening.get_all()
    return str(len(screenings))
