# -*- coding: utf-8 -*-
import datetime as dt

from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    Model,
    SurrogatePK,
)


class MailingList(SurrogatePK, Model):
    """
    Model for mailing list.
    """
    __tablename__ = 'mailing_list'

    # Columns
    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    email = Column(db.String(80), unique=True, nullable=False)
    uploaded_at = Column(db.DateTime, nullable=False,
                         default=dt.datetime.utcnow)

    def __repr__(self):
        return '<MailingList()>'
