# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located
in app.py
"""

from flask_login import LoginManager
login_manager = LoginManager()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from celery import Celery
celery = Celery()

from flask_marshmallow import Marshmallow
ma = Marshmallow()

from flask_migrate import Migrate
migrate = Migrate()

from flask_caching import Cache
cache = Cache()

from flask_mail import Mail
mail = Mail()

from flask_jwt_extended import JWTManager
jwt = JWTManager()
