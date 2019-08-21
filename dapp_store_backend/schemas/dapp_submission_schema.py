from dapp_store_backend.extensions import ma
from dapp_store_backend.models.dapp_submission import DappSubmission


class DappSubmissionSchema(ma.ModelSchema):
    """
    Schema for DappSubmission object.
    """
    class Meta:
        model = DappSubmission
