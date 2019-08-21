# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    Model,
    relationship,
    SurrogatePK,
)


class Blockchain(SurrogatePK, Model):
    """
    Model for blockchains.
    """
    __tablename__ = 'blockchain'

    # Columns
    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    name = Column(db.String(32), unique=True, nullable=False)
    symbol = Column(db.String(16), unique=True, nullable=False)

    # Relationships to other tables
    dapps = relationship('Dapp', back_populates='blockchain', lazy='noload')
    users = relationship(
        'User', back_populates='blockchain', lazy='noload')
    block_intervals = relationship(
        'BlockInterval', back_populates='blockchain', lazy='noload')

    def __repr__(self):
        return '<Blockchain({id})>'.format(id=self.symbol)
