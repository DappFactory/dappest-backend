# -*- coding: utf-8 -*-
"""Private API unit tests."""
import json
import pytest

from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.models.metric import Metric
from dapp_store_backend.schemas.metric_schema import MetricSchema

TEST_USERS_COUNT = 100
TEST_VOLUME_COUNT = 100
TEST_TRANSACT_COUNT = 100

@pytest.mark.usefixtures('session')
def test_add_metric(session):
    """
    Test adding metrics for a dapp.
    """

    # initialize test client and the necessary schemas
    client = session.app.test_client()
    metric_schema = MetricSchema()

    # payload to send to the test client
    payload = {
        'metrics': [
            {
                'dapp_id': 1,
                'block_interval_id': 1,
                'metrics': {
                    'users': TEST_USERS_COUNT,
                    'volume': TEST_VOLUME_COUNT,
                    'transactions': TEST_TRANSACT_COUNT,
                }
            }
        ]
    }

    # what is our expected return from our db when we fetch the metrics
    expected = {
        'id': 1,
        'block_interval': 1,
        'data': {
            'users': TEST_USERS_COUNT,
            'volume': TEST_VOLUME_COUNT,
            'transactions': TEST_TRANSACT_COUNT,
        }
    }

    # run client upload and obtain response
    response = client.post('/api/v1/private/metric/add',
                           data=json.dumps(payload),
                           follow_redirects=True,
                           content_type='application/json')

    # get the "inserted" data by id
    retrieved = Metric.get_by_id(1)
    assert response.status_code == HTTPCodes.Success.value
    assert metric_schema.dump(retrieved).data == expected

