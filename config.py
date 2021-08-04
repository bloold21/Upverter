import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POST_PER_PAGE = 3
    ALI_ACCESSKEY_ID = os.environ.get('ALI_ACCESSKEY_ID')
    ALI_ACCESSKEY_SECRET = os.environ.get('ALI_ACCESSKEY_SECRET')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')