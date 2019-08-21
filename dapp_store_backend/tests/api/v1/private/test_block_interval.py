# -*- coding: utf-8 -*-
"""Private API unit tests."""
from datetime import datetime
import json
import pytest

from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.models.block_interval import BlockInterval
from dapp_store_backend.schemas.block_interval_schema import BlockIntervalSchema


@pytest.mark.usefixtures('session')
def test_add_blockinterval(session):
    """
    Test add block interval.
    """
    # initialize test client and the necessary schemas
    client = session.app.test_client()
    blockinterval_schema = BlockIntervalSchema()

    # payload to send to the test client
    payload = {
        'blockchain_id': 1,
        'time_start': 86400,
        'time_stop': 186400,
        'block_start': 1000,
        'block_stop': 1500
    }

    next_id = session.execute(
        "SELECT CURRVAL('block_interval_id_seq');").scalar() + 1

    # what is our expected return from our db when we fetch the metrics
    expected = {
        'id': next_id,
        'blockchain_id': 1,
        'time_start': 86400,
        'time_stop': 186400,
        'block_start': 1000,
        'block_stop': 1500
    }

    # run client upload and obtain response
    response = client.post('/api/v1/private/block_interval/add',
                           data=json.dumps(payload),
                           follow_redirects=True,
                           content_type='application/json')

    # get the data out of the model from the db
    retrieved = BlockInterval.get_by_id(next_id)
    assert response.status_code == HTTPCodes.Success.value
    assert blockinterval_schema.dump(retrieved).data == expected

# @pytest.mark.usefixtures('session')
# def test_get_blockinterval(session):
#     """
#     Test getting block interval from the database.
#     :param session:
#     :return:
#     """
#     # initialize test client and the necessary schemas
#     client = session.app.test_client()
#     blockchain_schema = BlockchainSchema()
#
#     # payload to send to the test client
#     payload = {
#     }
#
#     # what is our expected return from our db when we fetch the metrics
#     expected = {
#     }
#
#     # run client upload and obtain response
#     response = client.post()
#
#     pass
#
# @pytest.mark.usefixtures('session')
# def test_update_blockinterval(session):
#     """
#         Test getting block interval from the database.
#         :param session:
#         :return:
#         """
#     # initialize test client and the necessary schemas
#     client = session.app.test_client()
#     blockchain_schema = BlockchainSchema()
#
#     # payload to send to the test client
#     payload = {
#     }
#
#     # what is our expected return from our db when we fetch the metrics
#     expected = {
#     }
#
#     # run client upload and obtain response
#     response = client.post()
#
#     pass