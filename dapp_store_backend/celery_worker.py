# -*- coding: utf-8 -*-
"""
The worker module.
"""
from os import environ
from .settings import DevConfig, ProdConfig
from .app import celery, create_app

if environ.get("DAPP_STORE_BACKEND_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

app.app_context().push()

