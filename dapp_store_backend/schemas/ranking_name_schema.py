from dapp_store_backend.extensions import ma
from dapp_store_backend.models.ranking_name import RankingName


class RankingNameSchema(ma.ModelSchema):
    """
    Schema for RankingName object.
    """
    class Meta:
        model = RankingName
