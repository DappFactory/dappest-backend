# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    relationship,
    Column,
    Model,
    SurrogatePK
)


class RankingName(SurrogatePK, Model):
    """
    Model for all ranking names.
    """
    __tablename__ = 'ranking_name'

    id = Column(db.SmallInteger, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    name = Column(db.String(32), unique=True, nullable=False)

    ranking = relationship('Ranking', back_populates='ranking_name', lazy='noload')

    def __repr__(self):
        return '<RankingName({name})>'.format(name=self.name)
