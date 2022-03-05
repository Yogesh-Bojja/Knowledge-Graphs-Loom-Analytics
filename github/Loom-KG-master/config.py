import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DB_URI = os.environ.get('DATABASE_URL')
    DB_USER = os.environ.get('DATABASE_USERNAME')
    DB_PASS = os.environ.get('DATABASE_PASSWORD')
