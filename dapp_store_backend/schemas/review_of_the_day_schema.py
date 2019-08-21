from marshmallow import fields, post_dump

from dapp_store_backend.extensions import ma
from dapp_store_backend.models.review import Review
from .dapp_schema import DappSchema
from .user_schema import UserSchema
from .review_like_schema import ReviewLikeSchema


class ReviewOfTheDaySchema(ma.ModelSchema):
    """
    Schema for Review Of The Day object.
    """
    user = fields.Nested(UserSchema, only='username')
    helpful_votes = fields.Nested(ReviewLikeSchema, only='user_id', many=True)
    helpful_count = fields.Method('count_helpful_votes')
    dapp_name = fields.Method('flatten_dapp_name')
    dapp_logo = fields.Method('flatten_dapp_logo')

    class Meta:
        model = Review
        exclude = ('data',)

    @staticmethod
    def count_helpful_votes(obj):
        return len(obj.helpful_votes)

    @staticmethod
    def flatten_dapp_name(obj):
        return obj.dapp.name

    @staticmethod
    def flatten_dapp_logo(obj):
        return obj.dapp.logo_url

    @post_dump
    def sort_helpful_votes(self, obj):
        obj['helpful_votes'] = sorted(obj['helpful_votes'])
        return obj
