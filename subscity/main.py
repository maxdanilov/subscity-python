from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://subscity:subscity@127.0.0.1:3307/subscity-test?charset=utf8'
DB = SQLAlchemy(app)

@app.route('/')
def hello_world():
    return 'Hello, World!' + str(Yap.CITIES)
