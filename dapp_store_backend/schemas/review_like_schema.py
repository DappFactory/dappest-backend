from dapp_store_backend.extensions import ma
from dapp_store_backend.models.review_like import ReviewLike


class ReviewLikeSchema(ma.ModelSchema):
    """
    Schema for Review object.
    """
    class Meta:
        model = ReviewLike
