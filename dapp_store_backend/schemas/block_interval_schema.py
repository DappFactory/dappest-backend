from marshmallow import fields

from dapp_store_backend.extensions import ma
from dapp_store_backend.models.block_interval import BlockInterval


class BlockIntervalSchema(ma.ModelSchema):
    """
    Schema for Block object.
    """
    blockchain_id = fields.Integer()

    class Meta:
        model = BlockInterval
        exclude = ("metrics", "blockchain")
