from marshmallow import fields

from dapp_store_backend.extensions import ma
from dapp_store_backend.models.ranking import Ranking


class RankingSchema(ma.ModelSchema):
    """
    Schema for Ranking object.
    """
    name = fields.String()

    class Meta:
        model = Ranking
