from requests import session
from requests.exceptions import ConnectionError
from werkzeug.exceptions import BadRequest

from .utilities import combine_dict_same_keys
from dapp_store_backend.worker.services.base import BaseService
from dapp_store_backend.enums.status import HTTPCodes


class EthercanJSON(object):
    get_balance_fields = {
        'status',
        'message',
        'result',
    }

    get_transactions_fields = {
        'total_pages',
        'total_entries',
        'page_size',
        'page_number',
    }

    get_latest_block_fields = {
        'jsonrpc',
        'id',
        'latest_block',
    }


class Etherscan(BaseService):

    API_PREFIX = 'https://api.etherscan.io/api?'

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = session()

    def _get(self, url):
        # TODO: deal with "unknown exception" error
        try:
            response = self.session.get(url)
        except ConnectionError:
            raise ConnectionError

        if response.status_code == HTTPCodes.Success.value:
            # Check for empty response
            if response.text:
                data = response.json()
                return data

        raise BadRequest(
            'Problem with connection, status code: {}'.format(response.status_code))

    def get_balance(self, address, INWEI=False):
        """
        Function to get ether balance in WEI = 10^(-18) ether

        :param address:
        :return: (float) of the balance of ether or wei
        """
        url = self.API_PREFIX + 'module=account&action=balance&address={address}&tag=latest&apikey={api_key}'.format(address=address,
                                                                                                                     api_key=self.api_key)

        response = self._get(url)

        # if response is valid
        if int(response['status']) == 1:
            wei_balance = float(response.get('result'))
        else:
            raise BadRequest("Problem with getting balance! {}: {}".format(response['message'], response['result']))

        # return in WEI or ether
        if not INWEI:
            balance = wei_balance * 10.0e-18
        else:
            balance = wei_balance
        return balance

    def get_latest_block(self):
        """
        Function to return the latest block

        :return:
        """
        url = self.API_PREFIX + 'module=proxy&action=eth_blockNumber&apikey={api_key}'.format(api_key=self.api_key)
        response = self._get(url)

        # extract response
        latest_block = int(response['result'], 0)

        return latest_block

    def get_transactions(self, address, block_start, block_stop, paginate=False, page=1, offset=10):

        url = self.API_PREFIX + 'module=account&action=txlist&address={address}&startblock={block_start}&endblock={block_stop}&sort=asc&apikey={api_key}'.format(
            address=address, block_start=block_start, block_stop=block_stop, api_key=self.api_key)

        if paginate:
            url += '&page={page}&offset={offset}'.format(
                page=page, offset=offset)

        response = self._get(url)
        return response.get('result')

    def process_transactions(self, func, address, block_start, block_stop, full=False):

        page = 1
        transactions = self.get_transactions(
            address, block_start, block_stop, paginate=True, page=page, offset=10000)

        results = func(transactions)
        print('Processed {} transactions'.format(len(transactions)))

        try:
            while len(transactions) == 10000:

                page += 1
                transactions = self.get_transactions(
                    address, block_start, block_stop, paginate=True, page=page, offset=10000)

                results = combine_dict_same_keys(results, func(transactions))

                print('Processed {} transactions from page {}.'.format(
                    len(transactions), page))
        except Exception as e:  # TODO: specify exception
            print('ERROR: {}'.format(e))
            return {}

        return results
