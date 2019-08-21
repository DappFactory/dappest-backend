from os.path import join
from web3 import Web3
from decimal import Decimal
from flask import current_app
from marshmallow import fields, post_dump
from marshmallow.utils import get_value, missing

from dapp_store_backend.extensions import ma
from dapp_store_backend.enums.blockchains import BlockchainEnum
from .ranking_schema import RankingSchema


class DappListSchema(ma.ModelSchema):
    """
    Schema for list of dapps.
    """

    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    url = fields.String(dump_only=True)
    category = fields.String(dump_only=True)
    blockchain = fields.String(dump_only=True)
    rating = fields.Decimal(default=0, places=1, as_string=True)
    rating_count = fields.Integer(default=0, dump_only=True)
    tagline = fields.String(dump_only=True)
    description = fields.String(dump_only=True)
    symbol = fields.String(dump_only=True)
    logo_url = fields.Method(serialize='generate_logo_url')
    uploaded_at = fields.DateTime(dump_only=True)
    metrics = fields.Dict(default={
        'users': 0,
        'volume': 0,
        'transactions': 0}
    )
    rankings = fields.Nested(RankingSchema, many=True, only=['name', 'rank'])

    @classmethod
    def get_attribute(cls, attr, obj, default):
        return get_value(attr, obj, default=default) or missing

    @staticmethod
    def generate_logo_url(obj):
        return join(current_app.config['S3_BUCKET_PATH'], obj.logo_path)

    @post_dump
    def convert_rating_to_float(self, obj):
        obj['rating'] = float(obj['rating'])
        return obj

    @post_dump
    def format_volume_metrics(self, obj):
        metrics = obj.get('metrics')

        if metrics:
            volume = metrics.get('volume')
            if volume:
                if obj.get('blockchain') == BlockchainEnum.ETH.name and volume > 0:
                    obj['metrics']['volume'] = float(Decimal(Web3.fromWei(obj.get('metrics').get('volume'), 'ether'))
                                                     .quantize(Decimal('0.00001')))

        return obj


