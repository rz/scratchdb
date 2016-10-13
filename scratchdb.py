### A simple key-value database that supports set, get, and pop operations.


# The physical layer
class FileStorage(object):
    def __init__(self, filename):
        pass

    # internal methods go here

    # the external api
    def read(self, address):
        pass

    def append(self, data):
        pass


# The logical layer
class Logical(object):
    pass


# The database API
class ScratchDB(object):
    pass


class QueryProcessor(object):
    pass


class Client(object):
    pass

