# -*- coding: utf-8 -*-
"""
The app module, containing the app factory function.
"""
from flask import Blueprint, Flask
from flask_restplus import Api
from flask_cors import CORS

from .settings import DevConfig, CeleryConfig
from .extensions import (
    cache,
    celery,
    db,
    jwt,
    login_manager,
    ma,
    mail,
    migrate
)
from .api.v1.common import api as common_api
from .api.v1.public import dapp as public_dapp, review as public_review, user
from .api.v1.private import (block_interval, blockchain, category,
                             dapp as private_dapp, dapp_submission, metric)


def create_app(config_object=DevConfig):
    """
    An application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    :param config_object: The configuration object to use.
    """
    # Create flask app
    app = Flask(__name__)
    cors = CORS(app, origins=config_object.CORS_ORIGIN)
    app.config.from_object(config_object)

    # Configure api
    blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
    api = Api(blueprint, title='Dappest API',
              version='1.0',
              description='Public and private API endpoints for Dappest.',
              endpoint='/api/v1')

    # Set up DB connection
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'.format(
            POSTGRES_USER=config_object.POSTGRES_USER,
            POSTGRES_PASSWORD=config_object.POSTGRES_PASSWORD,
            POSTGRES_HOST=config_object.POSTGRES_HOST,
            POSTGRES_PORT=config_object.POSTGRES_PORT,
            POSTGRES_DB=config_object.POSTGRES_DB)

    app.register_blueprint(blueprint)
    initialize_namespaces(api)
    register_extensions(app)

    # Configure celery
    celery.config_from_object(CeleryConfig)
    initialize_celery(app)

    return app


def initialize_celery(app):

    # create context tasks in celery
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return None


def register_extensions(app):
    cache.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    return None


def initialize_namespaces(api):
    api.namespaces.clear()
    api.add_namespace(common_api)
    api.add_namespace(public_dapp.api)
    api.add_namespace(public_review.api)
    api.add_namespace(user.api)
    api.add_namespace(block_interval.api)
    api.add_namespace(blockchain.api)
    api.add_namespace(category.api)
    api.add_namespace(private_dapp.api)
    api.add_namespace(dapp_submission.api)
    api.add_namespace(metric.api)
    return None


