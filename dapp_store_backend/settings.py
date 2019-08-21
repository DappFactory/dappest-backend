# -*- coding: utf-8 -*-
import os
from celery.schedules import crontab


def get_env_variable_list(name):
    var = os.environ.get(name)
    return var.split(',') if var else []


class Config(object):

    # Database settings
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    NETWORK_NAME = os.environ.get("NETWORK_ALIAS")

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('DAPP_STORE_BACKEND_SECRET', 'secret-key')  # TODO: Change me

    # Metrics interval
    BLOCK_INTERVAL_SECONDS = 60

    # User authorization secret
    JWT_TOKEN_SECRET = os.environ.get("JWT_TOKEN_SECRET")

    # AWS settings
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
    S3_BUCKET_PATH = os.environ.get("S3_BUCKET_PATH")

    # Ranking settings
    RATING_WEIGHT = 0.4
    USER_WEIGHT = 0.2
    VOLUME_WEIGHT = 0.2
    TRANSACTION_WEIGHT = 0.2
    MAX_REVIEW_COUNT = 100
    MAX_RANKING = 20

    # CORS settings
    CORS_ORIGIN = get_env_variable_list("CORS_ORIGIN")

    # Rating settings
    RATING_TYPES = ['usability', 'value', 'innovation']

    # API keys
    ETHERSCAN_API_KEY = ''
    INFURA_API_KEY = ''

    # etherscan api constants
    MAXETHERSCAN_LIMIT = 10000  # max number of transcations return
    ETHERSCAN_RATE_LIMIT = 5

    # Other settings
    PROPAGATE_EXCEPTIONS = True
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    MAIL_SERVER = ''
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = ''
    GOOGLE_ANALYTICS = ''

    CSRF_ENABLED = True


class CeleryConfig(Config):
    # Celery settings
    broker_url = ['amqp://{broker_hostname}:5672//vhost1'.format(broker_hostname=x)
                  for x in get_env_variable_list('CELERY_BROKER_HOSTNAME')]
    result_backend = 'rpc://'
    imports = ('dapp_store_backend.worker.tasks',)
    task_soft_time_limit = 60
    task_time_limit = 120


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False

    # Review settings
    VERIFIED_USER_MIN_TRANSACTIONS_THRESHOLD = 10
    VERIFIED_USER_MIN_OUT_VOLUME_THRESHOLD = 0.1

    # Metrics settings
    PERIODIC_TASK_TIME = crontab(hour=0, minute=0)
    BLOCK_INTERVAL_UNIT = 'day'
    FETCHER_BLOCK_INTERVAL = 86400


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True

    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

    # Review settings
    VERIFIED_USER_MIN_TRANSACTIONS_THRESHOLD = 0  # set to 10 for production
    VERIFIED_USER_MIN_OUT_VOLUME_THRESHOLD = 0  # set to 0.1 for production

    # Metrics settings
    PERIODIC_TASK_TIME = 60
    BLOCK_INTERVAL_UNIT = 'minute'
    FETCHER_BLOCK_INTERVAL = 60


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
