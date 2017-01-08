import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

DB_PATH = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(DB_USER, DB_PASS, DB_HOST, DB_PORT,
                                                               DB_NAME)
APP = Flask(__name__)
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
DB = SQLAlchemy(APP)


@APP.route('/')
def hello_world():
    return 'Hello, World!' + str(Yap.CITIES)
