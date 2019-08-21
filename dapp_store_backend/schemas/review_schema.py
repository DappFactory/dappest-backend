from marshmallow import fields, post_dump

from dapp_store_backend.extensions import ma
from dapp_store_backend.models.review import Review
from .review_like_schema import ReviewLikeSchema


class ReviewSchema(ma.ModelSchema):
    """
    Schema for Review object.
    """
    user = fields.Nested('UserSchema', only=['username', 'review_count'])
    helpful_votes = fields.Nested(ReviewLikeSchema, only='user_id', many=True)
    helpful_count = fields.Method('count_helpful_votes')

    class Meta:
        model = Review
        exclude = ('data',)

    @staticmethod
    def count_helpful_votes(obj):
        return len(obj.helpful_votes)

    @post_dump
    def sort_helpful_votes(self, obj):
        obj['helpful_votes'] = sorted(obj['helpful_votes'])
        return obj

