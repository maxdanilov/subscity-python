# -*- coding: utf-8 -*-
import os

from flask_sqlalchemy import SQLAlchemy

from subscity.app import get_app

DB_URI = os.environ.get('DB_URI')

APP = get_app()
DB = SQLAlchemy(APP)
