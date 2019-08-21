# -*- coding: utf-8 -*-
"""Private API unit tests."""

import pytest
from werkzeug.exceptions import BadRequest
import os

from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.worker.services.neoscan import Neoscan

from dapp_store_backend.settings import DevConfig, ProdConfig

if os.environ.get("DAPP_STORE_BACKEND_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig

TEST_NEO_ADDRESS = 'B6nRXSAPgjVGFmeA3WjCzwuMhCr2ZeFmg1eReufMaN9C'
TEST_NEO_API_KEY = ''


# @pytest.mark.usefixtures('session')
def test_get_balance():
    """
    Test getting balance for neoscanner

    :return:
    """
    neoscanner = Neoscan(TEST_NEO_API_KEY)

    # test a valid address
    balance = neoscanner.get_balance(TEST_NEO_ADDRESS)
    assert isinstance(balance, list)

    # if balance is not empty
    if balance:
        assert len(balance) == 2
        # loop through the types of unspent tokens
        for transactions in balance:
            # extract the json data
            asset = transactions['unspent']
            amount = transactions['amount']
            unspent = transactions['unspent']

            # TODO say something about this

    # test invalid address
    with pytest.raises(BadRequest) as excinfo:
        neoscanner.get_balance('failing_address')
    assert str(HTTPCodes.Bad_Request.value) in str(excinfo.value)

def test_get_transactions():
    """
    Test getting balance for neoscanner

    :return:
    """
    neoscanner = Neoscan(TEST_NEO_API_KEY)

    # test a valid address
    transactions = neoscanner.get_balance(TEST_NEO_ADDRESS)

    # if transactions exist
    if transactions:
        assert len(transactions) == 2
        # loop through the types of unspent tokens
        for transacts in transactions:
            # extract the json data
            txid = transacts['unspent']
            time = transacts['amount']
            block_height = transacts['unspent']
            asset = transacts['asset']
            amount = transacts['amount']
            address_to = transacts['address_to']
            address_from = transacts['address_from']

            # TODO say something about this
    
    assert isinstance(transactions, list)

    # test invalid address
    with pytest.raises(BadRequest) as excinfo:
        neoscanner.get_balance('failing_address')
    assert str(HTTPCodes.Bad_Request.value) in str(excinfo.value)

def test_get_all_nodes():
    """
    Test get all NEO nodes.
    :param session:
    :return:
    """
    # TODO: place neoscan initialization in a pytest.fixture with session scope so you only have to instantiate once
    neoscanner = Neoscan(TEST_NEO_API_KEY)

    nodes = neoscanner.get_all_nodes()

    # test for the json objects
    for node in nodes:
        assert 'url' in node.keys()
        assert 'height' in node.keys()

    assert isinstance(nodes, list)

    # test invalid address
    with pytest.raises(BadRequest) as excinfo:
        neoscanner.get_balance('failing_address')
    assert str(HTTPCodes.Bad_Request.value) in str(excinfo.value)
