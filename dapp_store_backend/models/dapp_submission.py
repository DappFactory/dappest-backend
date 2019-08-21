# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
import datetime as dt
from dapp_store_backend.database import (
    ARRAY,
    JSONB,
    UUID,
    Column,
    Model,
    SurrogatePK,
)


class DappSubmission(SurrogatePK, Model):
    """
    Model for all dapp submissions.
    """
    __tablename__ = 'dapp_submission'

    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    name = Column(db.String(80), unique=False, nullable=False)
    url = Column(db.String(80), unique=False, nullable=False)
    address = Column(ARRAY(db.String), unique=False, nullable=False)
    blockchain_id = Column(db.Integer, db.ForeignKey('blockchain.id'), unique=False, nullable=False)
    category_id = Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=False)
    user_id = Column(db.Integer, db.ForeignKey('dappest_user.id'), nullable=False)
    author = Column(ARRAY(db.String), unique=False, nullable=False)
    email = Column(db.String(80), unique=False, nullable=False)
    logo_path = Column(db.String(100), unique=False, nullable=False)
    screenshot = Column(ARRAY(db.String), unique=True, nullable=False)
    tagline = Column(db.String(80), unique=False, nullable=False)
    description = Column(db.String(500), unique=False, nullable=False)
    whitepaper = Column(db.String(160), unique=True, nullable=True, default=None)
    social_media = Column(JSONB, unique=False, nullable=False, default={})
    s3_id = Column(UUID, unique=True, nullable=False)
    status = Column(db.SmallInteger, unique=False, nullable=False,
                    default=0)
    uploaded_at = Column(db.DateTime, nullable=False,
                         default=dt.datetime.utcnow)
    launch_date = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __repr__(self):
        return '<DappSubmission({id})>'.format(id=self.id)
