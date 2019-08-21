# -*- coding: utf-8 -*-
import datetime as dt

from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    Column,
    Model,
    relationship,
    SurrogatePK,
)


class ReviewLike(SurrogatePK, Model):
    """
    Model for review likes (helpful/not helpful).
    """
    __tablename__ = 'review_like'
    __table_args__ = (db.UniqueConstraint('user_id', 'review_id', 'helpful'), )

    # Columns
    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    dapp_id = Column(db.Integer, db.ForeignKey('dapp.id'), unique=False, nullable=False)
    user_id = Column(db.Integer, db.ForeignKey('dappest_user.id'), unique=False, nullable=False)
    review_id = Column(db.Integer, db.ForeignKey('review.id'), unique=False, nullable=False)
    helpful = Column(db.SmallInteger, unique=False, nullable=False)
    created_at = Column(db.DateTime, nullable=False,
                        default=dt.datetime.utcnow)

    user = relationship('User', back_populates='review_likes', lazy='select')

    def __repr__(self):
        return '<ReviewLike()>'
