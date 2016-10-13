### A simple key-value database that supports set, get, and pop operations.

import os


# The physical layer
class FileStorage(object):
    INTEGER_FORMAT = '!Q'
    INTEGER_LENGTH = 8  # in bytes, this has to be consistent with INTEGER_FORMAT, see https://docs.python.org/3.1/library/struct.html#format-characters
    # INTEGER_FORMAT = '!H'
    # INTEGER_LENGTH = 2

    def __init__(self, filename):
        # never truncate the file if it exists
        try:
            f = open(filename, 'bx+')  # x mode raises an exception if the file exists, see https://docs.python.org/3/library/functions.html#open
        except FileExistsError:
            f = open(filename, 'r+b')
        self._f = f

        # ensure there are zero bytes at the end of the file
        self._zero_end()

    # internal methods
    def _seek(self, offset, whence=0):
        """Wrapper around File.seek() for consistency."""
        return self._f.seek(offset, whence)

    def _seek_end(self):
        """Moves the stream position to the end of file and returns that address."""
        return self._f.seek(0, os.SEEK_END)

    def _is_empty(self):
        end_address = self._seek_end()
        return end_address == 0

    def _read(self, n):
        """Wrapper around File.read() for consistency."""
        return self._f.read(n)

    def _write(self, bs):
        """Wrapper around File.write() for consistency."""
        addr = self._f.write(bs)
        self._f.flush()
        return addr

    def _zero_end(self):
        """
        Writes zero bytes at the end of the file so that reading a 0 integer at
        the end will succeed.
        """
        if self._is_empty() or self._seek_end() < self.INTEGER_LENGTH:
            self._seek_end()
            self._write(b'\x00' * self.INTEGER_LENGTH)
        else:
            self._seek(-self.INTEGER_LENGTH, os.SEEK_END)
            last_bytes = self._read(self.INTEGER_LENGTH)
            if any([byte != b'\x00' for byte in last_bytes]):
                self._seek_end()
                self._write(b'\x00' * self.INTEGER_LENGTH)

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

