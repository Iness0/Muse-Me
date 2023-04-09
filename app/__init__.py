from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# from flask_mailman import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _1
import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from sendgrid import Mail
from config import Config
from elasticsearch import Elasticsearch
from redis import Redis
import rq

migrate = Migrate()
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _1('Please login to see this page')
mail = Mail()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    # mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH'], basic_auth=
    (app.config['ELASTICSEARCH_LOGIN'], app.config['ELASTICSEARCH_PASSWORD']), verify_certs=False)
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('muse_me-tasks', connection=app.redis)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='muse_me Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/muse_mes.log', maxBytes=1024,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)s)'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('muse_me start')

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models
