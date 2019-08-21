from dapp_store_backend.extensions import ma
from dapp_store_backend.models.metric import Metric


class MetricSchema(ma.ModelSchema):
    """
    Schema for Metric object.
    """
    class Meta:
        model = Metric
