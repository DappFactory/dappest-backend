from os.path import join
from flask import current_app
from marshmallow import fields

from dapp_store_backend.extensions import ma
from dapp_store_backend.models.user import User


class UserSchema(ma.ModelSchema):
    """
    Schema for User object.
    """

    profile_picture_url = fields.Method('generate_profile_picture_url')
    reviews = fields.Nested('ReviewSchema', many=True)
    review_count = fields.Method('count_reviews')

    class Meta:
        model = User

    @staticmethod
    def generate_profile_picture_url(obj):
        return join(current_app.config['S3_BUCKET_PATH'], obj.profile_picture) if obj.profile_picture else ''

    @staticmethod
    def count_reviews(obj):
        return len(obj.reviews) if obj.reviews else 0
