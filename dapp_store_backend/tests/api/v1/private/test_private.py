# -*- coding: utf-8 -*-
"""Private API unit tests."""
import json
import pytest

from dapp_store_backend.enums.status import HTTPCodes

from dapp_store_backend.models.blockchain import Blockchain
from dapp_store_backend.models.category import Category
from dapp_store_backend.schemas.blockchain_schema import BlockchainSchema
from dapp_store_backend.schemas.category_schema import CategorySchema


@pytest.mark.usefixtures('session')
def test_add_blockchain(session):
    """
    Test add blockchain.
    """

    client = session.app.test_client()
    blockchain_schema = BlockchainSchema()

    payload = {
        'name': 'TestBlockchain',
        'symbol': 'TBLK'
    }

    next_id = session.execute(
        "SELECT CURRVAL('blockchain_id_seq');").scalar() + 1

    expected = {
        'id': next_id,
        'name': 'TestBlockchain',
        'symbol': 'TBLK',
        'dapps': [],
        'users': [],
        'block_intervals': []
    }

    response = client.post('/api/v1/private/blockchain/add',
                           data=json.dumps(payload),
                           follow_redirects=True,
                           content_type='application/json')

    retrieved = Blockchain.get_by_id(next_id)
    assert response.status_code == HTTPCodes.Success.value
    assert blockchain_schema.dump(retrieved).data == expected


@pytest.mark.usefixtures('session')
def test_add_category(session):
    """
    Test add category.
    """

    client = session.app.test_client()
    category_schema = CategorySchema()

    payload = {
        'name': 'Social'
    }

    next_id = session.execute(
        "SELECT CURRVAL('category_id_seq');").scalar() + 1

    expected = {
        'id': next_id,
        'name': 'Social',
        'dapps': []
    }

    response = client.post('/api/v1/private/category/add',
                           data=json.dumps(payload),
                           follow_redirects=True,
                           content_type='application/json')

    retrieved = Category.get_by_id(next_id)
    assert response.status_code == HTTPCodes.Success.value
    assert category_schema.dump(retrieved).data == expected
