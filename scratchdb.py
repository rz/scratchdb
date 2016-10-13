### A simple key-value database that supports set, get, and pop operations.


# The physical layer
class FileStorage(object):
    def __init__(self, filename):
        # never truncate the file if it exists
        try:
            f = open(filename, 'bx+')  # x mode raises an exception if the file exists, see https://docs.python.org/3/library/functions.html#open
        except FileExistsError:
            f = open(filename, 'r+b')
        self._f = f

    # internal methods go here

    # the external api
    def read(self, address):
        pass

    def append(self, data):
        pass

    def close(self):
        self._f.close()


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

