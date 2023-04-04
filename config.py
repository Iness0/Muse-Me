import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_EMAIL = os.environ.get('SENDGRID_EMAIL')
    ADMINS = os.environ.get('ADMINS')
    POSTS_PER_PAGE = 7
    LANGUAGES = ['en', 'ru', 'he']
    ELASTICSEARCH = os.environ.get('ELASTICSEARCH_URL')
    ELASTICSEARCH_LOGIN = os.environ.get('ELASTICSEARCH_LOGIN')
    ELASTICSEARCH_PASSWORD = os.environ.get('ELASTICSEARCH_PASSWORD')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    STATIC_FOLDER = 'static'
    UPLOAD_FOLDER = 'app/static/uploads/'
    COMMENTS_AUTOLOAD = 3
    ALLOWED_FILES = {'png', 'jpg', 'jpeg', 'gif'}
