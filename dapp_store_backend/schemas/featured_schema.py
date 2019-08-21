from marshmallow import fields

from dapp_store_backend.extensions import ma
from dapp_store_backend.models.featured import Featured


class FeaturedSchema(ma.ModelSchema):
    """
    Schema for Featured Dapp object.
    """
    page = fields.String()
    dapp_id = fields.Integer()
    banner_url = fields.String()

    class Meta:
        model = Featured
        exclude = ('banner_path', 'page', 'duration', 'start_date', 'end_date')
