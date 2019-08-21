# -*- coding: utf-8 -*-
from datetime import datetime
import pytest

from dapp_store_backend.models.block_interval import BlockInterval


@pytest.mark.usefixtures('session')
class TestBlockInterval:
    """
    Test the block interval model.
    """

    def test_add_block_interval(self, session):
        block_interval = BlockInterval(blockchain_id=1,
                                       time_start=86400,
                                       time_stop=186400)

        session.add(block_interval)
        session.commit()

        retrieved = BlockInterval.query.get(block_interval.id)

        assert retrieved == block_interval
