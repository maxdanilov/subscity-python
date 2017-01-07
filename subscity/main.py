from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

DB_PATH = 'mysql+pymysql://subscity:subscity@127.0.0.1:3307/subscity-test?charset=utf8'
APP = Flask(__name__)
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
DB = SQLAlchemy(APP)


@APP.route('/')
def hello_world():
    return 'Hello, World!' + str(Yap.CITIES)
