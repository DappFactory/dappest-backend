class BaseService(object):
    def _get(self, url):
        raise NotImplementedError("Need to implement the get function for a "
                                  "scanning service.")

    def get_balance(self, address):
        raise NotImplementedError("Need to implement a function to get the balance"
                                  "of a specific address")

    def get_transactions(self, address, block_start, block_stop, paginate=False, offset=10):
        raise NotImplementedError("Need to implement a method to get transactions based on"
                                  "address, blockstart, blockstop")
