# -*- coding: utf-8 -*-
from dapp_store_backend.worker.constants import Metric


def wrap_result(result, message='Empty result.'):
    """
    Add states to result.
    """
    if result:
        return {'state': 1, 'message': '', 'result': result}
    else:
        return {'state': 0, 'message': message, 'result': {}}


def combine_dict_same_keys(dict1, dict2):
    """
    Combine two dicts with the same keys
    """
    assert dict1.keys() == dict2.keys(), 'Dicts have different keys.'
    return {x: dict1.get(x) + dict2.get(x) for x in dict1}


def extract_vt_from_transactions(transactions, from_address, to_address):
    """
    Get in_volume, out_volume, and number of transactions from Etherscan
    between two addresses.

    Args:
        transactions (list(str)): Etherscan get_transactions
        from_address (str): Originating ethereum address
        to_address (list(str)): Target ethereum addresses
    """

    tx_info = {'in_volume': 0,
               'out_volume': 0,
               'transactions': 0}

    for tx in transactions:

        tx_from_address = tx.get('from')
        tx_to_address = tx.get('to')
        value = tx.get('value')

        if tx_from_address == from_address and tx_to_address in to_address:
            tx_info['out_volume'] += int(value)
            tx_info['transactions'] += 1
        elif tx_from_address in to_address and tx_to_address == from_address:
            tx_info['in_volume'] += int(value)
            tx_info['transactions'] += 1

    return tx_info


def extract_uvt_from_transactions(transactions, address):
    """
    Get unique users, volume, number of transactions for single address.

    Args:
        transactions (list(str)): etherscan transactions
    """
    users = []
    volume = 0
    num_transactions = 0

    for tx in transactions:

        # Skip if transaction error
        if tx.get('txreceipt_status') != '1' or tx.get('isError') != '0':
            continue

        from_address = tx.get('from')
        to_address = tx.get('to')

        if from_address == address:
            users.append(to_address)
        else:
            users.append(from_address)

        volume += int(tx.get('value'))
        num_transactions += 1

    return {Metric.users.name: users,
            Metric.volume.name: volume,
            Metric.transactions.name: num_transactions}
