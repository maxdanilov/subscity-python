from flask import Flask
from subscity.yandex_afisha_parser import YandexAfishaParser as Yap

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!' + str(Yap.CITIES)
