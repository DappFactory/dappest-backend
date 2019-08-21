# -*- coding: utf-8 -*-
from dapp_store_backend.extensions import db
import datetime as dt
from dapp_store_backend.database import (
    Column,
    JSONB,
    Model,
    relationship,
    SurrogatePK,
)


class Review(SurrogatePK, Model):
    """
    Model for all dapp reviews.
    """
    __tablename__ = 'review'

    # Columns
    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    dapp_id = Column(db.Integer, db.ForeignKey('dapp.id'), nullable=False)
    user_id = Column(db.Integer, db.ForeignKey(
        'dappest_user.id'), nullable=False)
    rating = Column(db.SmallInteger, unique=False, nullable=False)
    title = Column(db.String(50), unique=False, nullable=False)
    review = Column(db.Text, unique=False, nullable=False)
    feature = Column(JSONB, unique=False, nullable=False, default={})
    uploaded_at = Column(db.DateTime, nullable=False,
                         default=dt.datetime.utcnow)
    data = Column(JSONB, unique=False, nullable=False, default={})
    verified = Column(db.Boolean, unique=False, nullable=False, default=False)

    dapp = relationship('Dapp', back_populates='reviews', lazy='select')
    user = relationship('User', back_populates='reviews', lazy='joined')
    helpful_votes = relationship('ReviewLike',
                                 primaryjoin='and_(Review.id==ReviewLike.review_id, '
                                             'ReviewLike.helpful==1)')
    # not_helpful_votes = relationship('ReviewLike',
    #                                  primaryjoin='and_(Review.id==ReviewLike.review_id, '
    #                                              'ReviewLike.helpful==0)')

    def __repr__(self):
        return '<Review({id})>'.format(id=self.id)
