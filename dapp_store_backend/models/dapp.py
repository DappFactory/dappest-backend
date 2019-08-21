# -*- coding: utf-8 -*-
from os.path import join
from flask import current_app
from dapp_store_backend.extensions import db
import datetime as dt
from dapp_store_backend.database import (
    ARRAY,
    JSONB,
    UUID,
    Column,
    hybrid_property,
    Model,
    relationship,
    SurrogatePK,
)


class Dapp(SurrogatePK, Model):
    """
    Model for all dapps.
    """
    __tablename__ = 'dapp'

    # Columns
    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    name = Column(db.String(80), unique=True, nullable=False)
    url = Column(db.String(80), unique=True, nullable=False)
    address = Column(ARRAY(db.String), unique=True, nullable=False)
    author = Column(ARRAY(db.String), unique=False, nullable=False)
    email = Column(db.String(80), unique=False, nullable=False)
    logo_path = Column(db.String(100), unique=True, nullable=False)
    screenshot = Column(ARRAY(db.String), unique=True, nullable=False)
    tagline = Column(db.String(80), unique=False, nullable=False)
    description = Column(db.String(500), unique=False, nullable=False)
    whitepaper = Column(db.String(160), unique=False, nullable=True, default=None)
    social_media = Column(JSONB, unique=False, nullable=False, default={})
    category_id = Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=False)
    blockchain_id = Column(db.Integer, db.ForeignKey(
        'blockchain.id'), nullable=False)
    user_id = Column(db.Integer, db.ForeignKey('dappest_user.id'), nullable=False)
    s3_id = Column(UUID, unique=True, nullable=False)
    uploaded_at = Column(db.DateTime, nullable=False,
                         default=dt.datetime.utcnow)
    launch_date = Column(db.DateTime, nullable=False)

    # Relationships to other tables
    blockchain = relationship('Blockchain', back_populates='dapps', lazy='select')
    category = relationship('Category', back_populates='dapps', lazy='select')
    reviews = relationship('Review', back_populates='dapp', lazy='subquery')
    user = relationship('User', back_populates='dapps', lazy='select')

    @hybrid_property
    def logo_url(self):
        return join(current_app.config['S3_BUCKET_PATH'], self.logo_path)

    @hybrid_property
    def screenshot_url(self):
        return [join(current_app.config['S3_BUCKET_PATH'], x) for x in self.screenshot]

    def __repr__(self):
        return '<Dapp({name})>'.format(name=self.name)
