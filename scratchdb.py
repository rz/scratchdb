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
        if self._is_empty():
            self._zero_end(128)
        else:
            self._seek(-1, os.SEEK_END)
            last_byte = self._read(1)
            if last_byte != b'\x00':
                self._zero_end(128)

    # methods that interact with the file itself ie the wrapper around it
    def _seek(self, offset, whence=0):
        """Wrapper around File.seek() for consistency."""
        return self._f.seek(offset, whence)

    def _seek_start(self):
        """Moves the stream position to the beginning of the file and returns that address."""
        return self._f.seek(0, os.SEEK_SET)

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

    # internal utility methods
    def _zero_end(self, n=1):
        """Writes zero bytes at the end of the file."""
        self._seek_end()
        self._write(b'\x00'* self.INTEGER_LENGTH * n)

    def _read_integer(self):
        """Reads an integer from the file at the current stream position."""
        bs = self._read(self.INTEGER_LENGTH)
        return struct.unpack(self.INTEGER_FORMAT, bs)[0]  # struct.unpack always returns a tuple

    def _write_integer(self, n):
        """Writes an integer to the file at the current stream position."""
        bs = struct.pack(self.INTEGER_FORMAT, n)
        self._write(bs)

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

