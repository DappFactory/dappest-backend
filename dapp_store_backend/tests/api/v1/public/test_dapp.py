"""Public review API unit tests."""
import pytest

from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.models.daily_item import DailyItem
from dapp_store_backend.models.dapp import Dapp
from dapp_store_backend.schemas.dapp_list_address_schema import DappListAddressSchema

@pytest.mark.usefixtures('session')
def test_list_dapps(session):
    """
    Test  how to list the dapps.
    :param session:
    :return:
    """
    # initialize test client and the necessary schemas
    client = session.app.test_client()
    dapp_list_address_schema = DappListAddressSchema(many=True)

    payload = {
        'dapps': {
            'id': 1,
            'symbol': 'eth',
            'address': 'fake',
        }
    }
    next_id = session.execute(
        "SELECT CURRVAL('dapp_id_seq');").scalar() + 1

    # initialize GET request for list of dapps
    response = client.get('/api/v1/private/dapp/list',
                          data=payload,
                          content_type='application/json',
                          follow_redirects=True)


    # get the data out of the model from the db
    retrieved = Dapp.get_by_id(next_id)
    assert response.status_code == HTTPCodes.Success.value
    assert DappListAddressSchema.dump(retrieved).data is list

@pytest.mark.usefixtures('session')
def test_get_dapp_of_theday(session):
    """
    Test dapp of the day endpoint.
    :param session:
    :return:
    """
    # initialize test client and the necessary schemas
    client = session.app.test_client()

    response = client.get('/api/v1/public/dapp/dapp_of_the_day',
                          follow_redirects=True)

    dapp_of_the_day_id = DailyItem.get_by_id(1)

    assert response.status_code == HTTPCodes.Success.value
    assert response.json.get('id') == dapp_of_the_day_id.item_id


@pytest.mark.usefixtures('session')
def test_change_dapp_of_theday(session):
    """
    Test review of the day endpoint.

    TODO:
    1. IS THIS THE CORRECT WAY TO TEST, SETTING SOMETHING?

    :param session:
    :return:
    """
    dapp_of_the_day_id = DailyItem.get_by_id(1)
    dapp_of_the_day_id.item_id = 2
    session.commit()

    # initialize test client and the necessary schemas
    client = session.app.test_client()

    response = client.get('/api/v1/private/dapp/dapp_of_the_day/set',
                          follow_redirects=True)

    dapp_id = DailyItem.get_by_id(1)

    assert response.status_code == HTTPCodes.Success.value
    assert response.json.get('id') == dapp_id.item_id
