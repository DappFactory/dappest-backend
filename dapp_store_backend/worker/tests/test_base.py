# -*- coding: utf-8 -*-
"""Private API unit tests."""
import pytest

from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.worker.services.base import BaseService

def test_baseclass():
    baseservice = BaseService()

    with pytest.raises(NotImplementedError):
        baseservice._get(url='')

    with pytest.raises(NotImplementedError):
        baseservice.get_balance(address='')

def test_httpcodes():
    """
    Test the http codes are exactly enumerated as 
    the numbers we intend.
    """
    assert HTTPCodes.Success.value == 200
    assert HTTPCodes.Bad_Request.value == 400
    assert HTTPCodes.Not_Found.value == 404
    assert HTTPCodes.Internal_Server_Error.value == 500