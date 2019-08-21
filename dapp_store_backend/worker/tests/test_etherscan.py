# -*- coding: utf-8 -*-
"""Private Worker service unit tests."""

import pytest
from werkzeug.exceptions import BadRequest
import os

from dapp_store_backend.worker.services.etherscan import Etherscan

from dapp_store_backend.settings import DevConfig, ProdConfig

if os.environ.get("DAPP_STORE_BACKEND_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig

TEST_ETHER_API_KEY = config.ETHERSCAN_API_KEY    
TEST_ETHER_ADDRESS = '0xA7a7899d944fE658c4B0a1803BAB2F490bd3849e'


# @pytest.mark.usefixtures('session')
def test_get_balance():
    """
    Test getting balance for etherscanner

    :return:
    """
    etherscanner = Etherscan(TEST_ETHER_API_KEY)

    # test a valid address
    balance = etherscanner.get_balance(TEST_ETHER_ADDRESS)
    assert isinstance(balance, float)

    # test invalid address
    with pytest.raises(BadRequest) as excinfo:
        etherscanner.get_balance('failing_address')


def test_get_latest_block():
    etherscanner = Etherscan(TEST_ETHER_API_KEY)

    # test a valid address
    latest_block = etherscanner.get_latest_block()
    assert isinstance(latest_block, int)

