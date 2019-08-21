# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    relationship,
    Column,
    Model,
    SurrogatePK
)


class Ranking(SurrogatePK, Model):
    """
    Model for all dapp rankings.
    """
    __tablename__ = 'ranking'

    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    dapp_id = Column(db.Integer, db.ForeignKey(
        'dapp.id'), unique=False, nullable=False)
    block_interval_id = Column(db.Integer, db.ForeignKey(
        'block_interval.id'), unique=False, nullable=False)
    ranking_name_id = Column(db.SmallInteger, db.ForeignKey('ranking_name.id'),
                             unique=False, nullable=False)
    rank = Column(db.SmallInteger, unique=False, nullable=False)

    ranking_name = relationship('RankingName', back_populates='ranking', lazy='joined')

    def __repr__(self):
        return '<Ranking({id})>'.format(id=self.id)
