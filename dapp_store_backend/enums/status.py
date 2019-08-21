from enum import Enum


class DappSubmissionStatus(Enum):

    SUBMITTED = 0
    APPROVED = 1
    DENIED = 2


class HTTPCodes(Enum):
    """
    TODO: Convert all HTTP Codes to this enumeration.

    """
    Success = 200
    Bad_Request = 400
    Not_Found = 404
    Internal_Server_Error = 500

