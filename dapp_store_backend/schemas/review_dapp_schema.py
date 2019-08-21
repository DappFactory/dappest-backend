from marshmallow import fields, post_dump

from dapp_store_backend.extensions import ma
from dapp_store_backend.models.review import Review
from .dapp_schema import DappSchema
from .user_schema import UserSchema
from .review_like_schema import ReviewLikeSchema


class ReviewDappSchema(ma.ModelSchema):
    """
    Schema for Review with dapp nested object.
    """
    user = fields.Nested(UserSchema, only='username')
    dapp = fields.Nested(DappSchema, only=['name', 'logo_url'])
    helpful_votes = fields.Nested(ReviewLikeSchema, only='user_id', many=True)
    helpful_count = fields.Method('count_helpful_votes')
    dapp_name = fields.Method('get_dapp_name')
    logo_url = fields.Method('get_logo_url')

    class Meta:
        model = Review
        exclude = ('data',)

    @staticmethod
    def count_helpful_votes(obj):
        return len(obj.helpful_votes)

    @staticmethod
    def get_dapp_name(obj):
        return obj.dapp.name

    @staticmethod
    def get_logo_url(obj):
        return obj.dapp.logo_url

    @post_dump
    def sort_helpful_votes(self, obj):
        obj['helpful_votes'] = sorted(obj['helpful_votes'])
        return obj

