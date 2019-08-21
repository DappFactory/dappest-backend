from web3 import Web3
from decimal import Decimal
from marshmallow import fields, post_dump

from dapp_store_backend.extensions import ma
from dapp_store_backend.settings import Config
from dapp_store_backend.utilities import round_float
from dapp_store_backend.models.dapp import Dapp
from dapp_store_backend.enums.blockchains import BlockchainEnum
from .review_schema import ReviewSchema
from .category_schema import CategorySchema
from .blockchain_schema import BlockchainSchema
from .ranking_schema import RankingSchema


class DappSchema(ma.ModelSchema):
    """
    Schema for Dapp object.
    """

    blockchain = fields.Nested(BlockchainSchema, only='symbol')
    category = fields.Nested(CategorySchema, only='name')
    logo_url = fields.String()
    screenshot_url = fields.List(fields.String())
    reviews = fields.Nested(ReviewSchema, many=True, only=['review', 'rating', 'id', 'uploaded_at', 'user',
                                                           'helpful_votes', 'feature', 'title', 'verified'])
    metrics = fields.Dict(default={
        'users': 0,
        'volume': 0,
        'transactions': 0})
    symbol = fields.String()
    ratings = fields.Method(serialize='bin_ratings')
    avg_rating = fields.Method(serialize='average_rating')
    featured_ratings = fields.Method(serialize='get_featured_ratings')
    rankings = fields.Nested(RankingSchema, many=True, only=['name', 'rank'])

    class Meta:
        model = Dapp
        exclude = ('email',)

    @staticmethod
    def bin_ratings(obj):
        binned = {1: 0,
                  2: 0,
                  3: 0,
                  4: 0,
                  5: 0}

        for review in obj.reviews:
            binned[review.rating] += 1

        return binned

    # TODO: don't iterate twice during serialization
    @staticmethod
    def average_rating(obj):
        num_reviews = len(obj.reviews)
        return 0 if not num_reviews else round_float(sum(x.rating for x in obj.reviews) / num_reviews)

    @staticmethod
    def get_featured_ratings(obj):

        ratings = {x: [] for x in Config.RATING_TYPES}

        for review in obj.reviews:
            features = review.feature

            for col in Config.RATING_TYPES:
                val = features.get(col)

                if val:
                    ratings[col].append(int(val))

        for col in Config.RATING_TYPES:
            ratings[col] = sum(ratings[col]) / len(ratings[col]) if ratings[col] else 0
            ratings[col] = round_float(ratings[col])

        return ratings

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
