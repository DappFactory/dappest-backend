from enum import Enum


class Network(Enum):

    mainnet = 1
    ropsten = 2
    infuranet = 3
    kovan = 4
    rinkeby = 5


class Metric(Enum):

    users = 1
    volume = 2
    transactions = 3
