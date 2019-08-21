"""Public review API unit tests."""
import json
import pytest

from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.models.daily_item import DailyItem
from dapp_store_backend.models.review import Review


@pytest.mark.usefixtures('session')
def test_review_of_the_day(session):
    """
    Test review of the day endpoint.
    :param session:
    :return:
    """

    client = session.app.test_client()

    response = client.get('/api/v1/public/review/review_of_the_day',
                          follow_redirects=True)

    review_of_the_day_id = DailyItem.get_by_id(1)

    assert response.status_code == HTTPCodes.Success.value
    assert response.json.get('id') == review_of_the_day_id.item_id


@pytest.mark.usefixtures('session')
def test_change_review_of_the_day(session):
    """
    Test review of the day endpoint.
    :param session:
    :return:
    """
    review_of_the_day_id = DailyItem.get_by_id(1)
    review_of_the_day_id.item_id = 2
    session.commit()

    client = session.app.test_client()

    response = client.get('/api/v1/public/review/review_of_the_day',
                          follow_redirects=True)

    review_id = DailyItem.get_by_id(1)

    assert response.status_code == HTTPCodes.Success.value
    assert response.json.get('id') == review_id.item_id

