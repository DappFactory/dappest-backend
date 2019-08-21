import datetime as dt
from uuid import uuid4
from dapp_store_backend.extensions import db
from dapp_store_backend.database import (
    UUID,
    Column,
    Model,
    relationship,
    SurrogatePK,
)
from dapp_store_backend.utilities import generate_nonce


def default_username(context):
    return context.get_current_parameters()['address']


class User(SurrogatePK, Model):
    """
    Model for all users.
    """
    __tablename__ = 'dappest_user'

    # Columns
    id = Column(db.Integer, unique=True, nullable=False,
                primary_key=True, autoincrement=True)
    address = Column(db.String(64), unique=True, nullable=False)
    username = Column(db.String(64), unique=True, nullable=False, default=default_username)
    email = Column(db.String(64), unique=False, nullable=True, default=None)
    profile_picture = Column(db.String(100), unique=False, nullable=True, default=None)
    blockchain_id = Column(db.Integer, db.ForeignKey(
        'blockchain.id'), nullable=False)
    s3_id = Column(UUID, unique=True, nullable=False, default=str(uuid4()))
    created_at = Column(db.DateTime, nullable=False,
                        default=dt.datetime.utcnow)
    nonce = Column(db.String(9), nullable=False, unique=False,
                   default=generate_nonce)

    # Relationships to other tables
    blockchain = relationship('Blockchain', back_populates='users', lazy='noload')
    reviews = relationship('Review', back_populates='user', lazy='noload')
    review_likes = relationship('ReviewLike', back_populates='user', lazy='noload')
    dapps = relationship('Dapp', back_populates='user', lazy='noload')

    def __repr__(self):
        return '<User({username!r})>'.format(username=self.username)

    @staticmethod
    def get_user_from_jwt_token(user_from_token):
        """
        Validate ideneity from jwt token.
        :param user_from_token:
        :return:
        """
        user_id = user_from_token.get('id')
        user_address = user_from_token.get('address')

        if user_id and user_address:
            user = User.get_by_id(user_id)

            if user and user.id == user_id and user.address == user_address:
                return user

        return None
