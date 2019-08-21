# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    Model,
    SurrogatePK,
)


class DailyItem(SurrogatePK, Model):
    """
    Model for items that change daily.
    """
    __tablename__ = 'daily_item'

    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    item_name = Column(db.String(32), unique=True, nullable=False)
    item_id = Column(db.Integer, unique=False, nullable=False, default=0)

    def __repr__(self):
        return '<DailyItem({name})>'.format(name=self.item_name)
