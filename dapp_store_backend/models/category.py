# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    Model,
    relationship,
    SurrogatePK,
)


class Category(SurrogatePK, Model):
    """
    Model for categories.
    """
    __tablename__ = 'category'

    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    name = Column(db.String(32), unique=True, nullable=False)

    dapps = relationship(
        'Dapp', back_populates='category', lazy='noload')

    def __repr__(self):
        return '<Category({name})>'.format(name=self.name)
