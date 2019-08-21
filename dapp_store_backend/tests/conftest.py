# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import pytest

from dapp_store_backend.settings import TestConfig
from dapp_store_backend.app import create_app
from dapp_store_backend.database import db as _db

from dapp_store_backend.models.user import User
from dapp_store_backend.models.blockchain import Blockchain
from dapp_store_backend.models.block_interval import BlockInterval
from dapp_store_backend.models.category import Category
from dapp_store_backend.models.dapp import Dapp
from dapp_store_backend.models.daily_item import DailyItem
from dapp_store_backend.models.review import Review


@pytest.fixture(scope='session')
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    _db.app = app

    with app.app_context():
        _db.create_all()

        initialize(_db)

    yield _db

    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    # TODO: remove - SUPER HACKY
    session.app = db.app

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


def initialize(db):
    """
    Initialize data to testing session to satisfy foreign key constraints.
    """
    blockchain = Blockchain(name='Bitcoin',
                            symbol='BTC')

    block_interval = BlockInterval(blockchain_id=1,
                                   time_start=0,
                                   time_stop=100,
                                   block_start=10,
                                   block_stop=20)

    user = User(address='0xb9D5ef5c0Cb313118da2960aE0F988Fe98699a31',
                username='0xb9D5ef5c0Cb313118da2960aE0F988Fe98699a31',
                blockchain_id=1,
                s3_id='7f1badea-9922-490c-bac8-fe06fdfa55a4')

    category = Category(name='Game')

    dapp = Dapp(name='CryptoKitties',
                url='cryptokitties.co',
                address=['0xb1690c08e213a35ed9bab7b318de14420fb57d8c'],
                author=['Brown Estate'],
                email='cryptokitties@gmail.com',
                logo_path='tmp.png',
                screenshot=['tmp1.png', 'tmp2.png'],
                tagline='Dapp tagline',
                description='Long descrption here.',
                category_id=1,
                blockchain_id=1,
                user_id=1,
                s3_id='0f0bedea-9922-490c-bac8-fe06fdfa55a4')

    review1 = Review(dapp_id=1,
                     user_id=1,
                     rating=1,
                     title='Best Dapp Ever',
                     review='Long review here.')

    review2 = Review(dapp_id=1,
                     user_id=1,
                     rating=1,
                     title='Worst Dapp Ever',
                     review='Very Long review here.')

    review_of_the_day = DailyItem(item_name='review_of_the_day',
                                  item_id=1)

    dapp_of_the_day = DailyItem(item_name='dapp_of_the_day',
                                item_id=1)

    db.session.add(blockchain)
    db.session.add(block_interval)
    db.session.add(user)
    db.session.add(category)
    db.session.add(dapp)
    db.session.add(review1)
    db.session.add(review2)
    db.session.add(review_of_the_day)
    db.session.add(dapp_of_the_day)
    db.session.commit()
