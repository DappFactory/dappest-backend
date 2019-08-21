from requests import session
from werkzeug.exceptions import BadRequest

from dapp_store_backend.worker.constants import Network
from dapp_store_backend.worker.services.base import BaseService
from dapp_store_backend.enums.status import HTTPCodes


class Infura(BaseService):
    """
    Wrapper class for Infura JSON RPC API.
    """

    def __init__(self, api_key,
                 network=Network.mainnet):
        self.api_key = api_key
        self.network = network
        self.session = session()

        self._init_url()

    def _init_url(self):
        """
        Initialize JSON RPC URL.
        """
        self.url = 'https://{network}.infura.io/{api_key}'.format(network=self.network.name,
                                                                  api_key=self.api_key)

    def _get(self, url):
        pass

    def _post(self, payload):
        """
        Post method.
        """
        # TODO: deal with "unknown exception" error
        try:
            response = self.session.post(self.url,
                                         json=payload)
        except ConnectionError:
            raise ConnectionRefusedError

        if response.status_code != HTTPCodes.Success.value and not response.text:
            raise BadRequest("Problem with connection, status code: %s" % response.status_code)

        return response.json()

    def get_block_number(self):
        """
        Returns the number of most recent block.

        Response:
        {
            jsonrpc: "2.0",
            id: 1,
            result: "0x5c174e"
        }
        """
        payload = {'jsonrpc': '2.0',
                   'id': 1,
                   'method': 'eth_blockNumber'}

        response = self._post(payload)

        try:
            return int(response.get('result'), 16)
        except ValueError:
            raise ValueError('Could not convert {} to integer.'.format(
                response.get('result')))

    def get_block_by_number(self, value):
        """
        Returns information about a block by block number.

        Params:
        value(int) : integer of a block number, or the string "earliest", "latest" or "pending"
        """
        if type(value) == int:
            try:
                value = hex(value)
            except ValueError:
                raise ValueError('Could not convert {} to hexadecimal.'.format(
                    value))
        elif value not in ['earliest', 'latest', 'pending']:
            raise ValueError('{} not valid choice.'.format(value))

        payload = {'jsonrpc': '2.0',
                   'method': 'eth_getBlockByNumber',
                   'params': [value, False],
                   'id': 1}

        response = self._post(payload)

        return response.get('result')
