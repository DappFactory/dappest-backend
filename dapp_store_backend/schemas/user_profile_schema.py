from os.path import join
from flask import current_app
from marshmallow import fields, post_dump

from dapp_store_backend.extensions import ma
from dapp_store_backend.models.user import User
from dapp_store_backend.schemas.blockchain_schema import BlockchainSchema
from dapp_store_backend.schemas.dapp_list_user_schema import DappListUserSchema
from dapp_store_backend.schemas.review_dapp_schema import ReviewDappSchema


class UserProfileSchema(ma.ModelSchema):
    """
    Schema for User profile object.
    """

    review_count = fields.Method('count_reviews')
    reviews = fields.Nested(ReviewDappSchema, many=True, exclude=('dapp',))
    blockchain = fields.Nested(BlockchainSchema, only='name')
    profile_picture_url = fields.Method('generate_profile_picture_url')
    ratings = fields.Method('bin_ratings')
    dapps = fields.Nested(DappListUserSchema, many=True)

    class Meta:
        model = User

    @staticmethod
    def count_reviews(obj):
        return len(obj.reviews)

    @staticmethod
    def bin_ratings(obj):
        binned = {1: 0,
                  2: 0,
                  3: 0,
                  4: 0,
                  5: 0}

        for review in obj.reviews:
            binned[review.rating] += 1

        return binned

    @staticmethod
    def generate_profile_picture_url(obj):
        return join(current_app.config['S3_BUCKET_PATH'], obj.profile_picture) if obj.profile_picture else ''

    @post_dump
    def count_review_likes(self, obj):
        reviews = obj.get('reviews')
        obj['review_like_count'] = sum([x.get('helpful_count') for x in obj.get('reviews')]) if not reviews else 0
        return obj
