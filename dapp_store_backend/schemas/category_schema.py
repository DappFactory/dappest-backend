from dapp_store_backend.extensions import ma
from dapp_store_backend.models.category import Category


class CategorySchema(ma.ModelSchema):
    """
    Schema for Category object.
    """
    class Meta:
        model = Category
