# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    Model,
    relationship,
    SurrogatePK
)


class BlockInterval(SurrogatePK, Model):
    """
    Model for all blockchain block intervals.
    """
    __tablename__ = 'block_interval'

    # TODO: add unique blockchain_id + timestamp restraint
    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    blockchain_id = Column(db.Integer, db.ForeignKey(
        'blockchain.id'), unique=False, nullable=False)
    time_start = Column(db.Integer, nullable=False)
    time_stop = Column(db.Integer, nullable=False)
    block_start = Column(db.Integer, nullable=False, default=0)
    block_stop = Column(db.Integer, nullable=False, default=0)

    blockchain = relationship('Blockchain', back_populates='block_intervals', lazy='joined')
    metrics = relationship('Metric', back_populates='block_interval', lazy='joined')

    def __repr__(self):
        return '<BlockInterval({id})>'.format(id=self.id)
