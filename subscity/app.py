import os

from flask import Flask


def get_app():
    app = Flask(__name__)
    db_uri = os.environ.get('DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    return app
