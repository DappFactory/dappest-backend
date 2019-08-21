from dapp_store_backend.extensions import ma
from dapp_store_backend.models.blockchain import Blockchain


class BlockchainSchema(ma.ModelSchema):
    """
    Schema for Blockchain object.
    """
    class Meta:
        model = Blockchain
