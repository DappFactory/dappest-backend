# -*- coding: utf-8 -*-
"""Private Worker service unit tests."""

import pytest
import os

from dapp_store_backend.worker.services.infura import Infura
from dapp_store_backend.settings import DevConfig, ProdConfig

if os.environ.get("DAPP_STORE_BACKEND_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig
TEST_INFURA_API_KEY = config.INFURA_API_KEY


# @pytest.mark.usefixtures('session')
def test_get_block_number():
    """
    Test getting balance for infura

    :return:
    """
    infura = Infura(TEST_INFURA_API_KEY)

    # test a valid address
    block_number = infura.get_block_number()
    assert isinstance(block_number, int)

def test_get_block_by_number():

    # test invalid address
    with pytest.raises(ValueError) as excinfo:
        infura.get_block_by_number('failing_value')

