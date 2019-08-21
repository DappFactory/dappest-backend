from marshmallow import fields

from dapp_store_backend.extensions import ma


class DappListAddressSchema(ma.ModelSchema):
    """
    Schema for list of dapps with address.
    """

    id = fields.Integer(dump_only=True)
    symbol = fields.String(dump_only=True)
    address = fields.List(fields.String())
