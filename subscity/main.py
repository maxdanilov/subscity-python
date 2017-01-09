import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

DB_URI = os.environ.get('DB_URI')
APP = Flask(__name__)
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
DB = SQLAlchemy(APP)


@APP.route('/')
def hello_world():
    return 'Hello, World!' + str(Yap.CITIES)
