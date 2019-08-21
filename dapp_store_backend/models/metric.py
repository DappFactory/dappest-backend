# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    JSONB,
    Model,
    relationship,
    SurrogatePK
)


class Metric(SurrogatePK, Model):
    """
    Model for all dapp metrics.
    """
    __tablename__ = 'metric'

    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    dapp_id = Column(db.Integer, db.ForeignKey(
        'dapp.id'), unique=False, nullable=False)
    block_interval_id = Column(db.Integer, db.ForeignKey(
        'block_interval.id'), unique=False, nullable=False)
    data = Column(JSONB, unique=False, nullable=False)

    block_interval = relationship('BlockInterval', back_populates='metrics', lazy='select')

    def __repr__(self):
        return '<Metric({name})>'.format(name=self.name)
