# -*- coding: utf-8 -*-
import pytest

from dapp_store_backend.models.blockchain import Blockchain


@pytest.mark.usefixtures('session')
class TestBlockchain:
    """
    Test for the blockchain model.
    """

    def test_get_by_id(self, session):
        blockchain = Blockchain(id=2,
                                name='Ethereum',
                                symbol='ETH')

        blockchain.save()

        retrieved = Blockchain.get_by_id(blockchain.id)
        assert retrieved == blockchain
