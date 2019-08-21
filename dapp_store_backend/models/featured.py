# -*- coding: utf-8 -*-
from os.path import join
from flask import current_app

from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    Model,
    hybrid_property,
    SurrogatePK,
)


class Featured(SurrogatePK, Model):
    """
    Model for featured dapps.
    """
    __tablename__ = 'featured'

    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    page = Column(db.SmallInteger, db.ForeignKey('category.id'), unique=False, nullable=False)
    position = Column(db.SmallInteger, unique=False, nullable=False)
    dapp_id = Column(db.Integer, db.ForeignKey('dapp.id'), nullable=False)
    banner_path = Column(db.String(100), unique=True, nullable=False)

    # TODO: consider change value type to decimal
    #bid_value = Column(db.Float, unique=False, nullable=False)
    #btc_value = Column(db.Float, unique=False, nullable=False)

    duration = Column(db.Integer, unique=False, nullable=False)
    start_date = Column(db.DateTime, unique=False, nullable=False)
    end_date = Column(db.DateTime, unique=False, nullable=False)

    @hybrid_property
    def banner_url(self):
        return join(current_app.config['S3_BUCKET_PATH'], self.banner_path)

    def __repr__(self):
        return '<Featured({id})>'.format(id=self.id)
