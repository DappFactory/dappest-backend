# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    Model,
    SurrogatePK,
)


class ContactForm(SurrogatePK, Model):
    """
    Model for contact form.
    """
    __tablename__ = 'contact_form'

    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    name = Column(db.String(32), unique=False, nullable=False)
    email = Column(db.String(80), unique=False, nullable=False)
    message = Column(db.String(1000), unique=False, nullable=False)

    def __repr__(self):
        return '<ContactForm()>'
