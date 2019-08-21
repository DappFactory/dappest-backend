from requests import session
from requests.exceptions import ConnectionError, RequestException
from werkzeug.exceptions import BadRequest
from dapp_store_backend.worker.services.base import BaseService
from dapp_store_backend.enums.status import HTTPCodes

class NeoscanJSON(object):
    get_balance_fields = {
        'balance',
        'address',
    }

    get_transactions_fields = {
        'total_pages',
        'total_entries',
        'page_size',
        'page_number',
    }

class Neoscan(BaseService):
    """
    Wrapper for Neoscan API.
    """

    API_PREFIX = 'https://api.neoscan.io/api?'
    TEST_API_PREFIX = 'https://neoscan-testnet.io/api/test_net/v1/'

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = session()

        self.API_PREFIX = self.TEST_API_PREFIX

    def _get(self, url):
        # TODO: deal with "unknown exception" error
        # establish the connection with session
        try:
            response = self.session.get(url)
        except ConnectionError:
            raise ConnectionError

        # check request status for success
        if response.status_code == HTTPCodes.Success.value:
            return response
        else:
            raise BadRequest("Problem with connection, status code: %s" % response.status_code)

    def get_balance(self, address):
        # define url
        url = self.API_PREFIX + 'get_balance/{address}/'.format(
            address=address)

        response = self._get(url)
        data = response.json()

        # extract data response - get balance, and address
        balance = data.get('balance')
        resp_address = data.get('address')

        assert resp_address == address

        # return if this was a success or not
        return balance

    def get_transactions(self, address):
        # always get first page
        page = 1
        # define url
        url = self.API_PREFIX + 'get_address_abstracts/{address}/'.format(
            address=address, page=page)

        response = self._get(url)
        data = response.json()

        # extract top level data
        total_pages = data['total_pages']
        total_entries = data['total_entries']
        page_size = data['page_size']
        page_number = data['page_number']

        # extract transactions
        transactions = []
        # go through all pages of transactions
        for i in range(total_pages):
            url = self.API_PREFIX + 'get_address_abstracts/{address}/'.format(
                address=address, page=i + 1)
            response = self._get(url)
            data = response.json()
            transactions.extend(data['entries'])

        return transactions

    def get_all_nodes(self):
        """
        Function to get all the nodes.
        Input:
        Output: list of dictionaries with keys (url, height)

        Returns all working nodes and their respective heights.
        Information is updated each minute.
        """
        url = self.API_PREFIX + 'get_all_nodes'
        response = self._get(url)
        data = response.json()

        nodes = data
        return nodes

    def get_transaction_summary(self, address, page):
        """
        /api/main_net/v1/get_address_abstracts/{address}/{page}
        """
        url = self.API_PREFIX + "/main_net/v1/get_address_abstracts/{0}/{1}".format(address, page)
        response = self._get(url)
        return response
