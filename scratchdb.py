### A simple key-value database that supports set, get, and pop operations.

import os
import pickle
import struct


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

    # methods that interact with the file itself ie the wrapper around it
    def _tell(self):
        """Wrapper around File.tell(). Returns the current stream position."""
        return self._f.tell()

    def _seek(self, offset, whence=0):
        """
        Wrapper around File.seek(). Moves the stream position to the
        indicated offset.
        """
        return self._f.seek(offset, whence)

    def _seek_start(self):
        """
        Moves the stream position to the beginning of the file and returns
        that address.
        """
        return self._f.seek(0, os.SEEK_SET)

    def _seek_end(self):
        """
        Moves the stream position to the end of file and returns that address.
        """
        return self._f.seek(0, os.SEEK_END)

    def _is_empty(self):
        end_address = self._seek_end()
        return end_address == 0

    def _read(self, n):
        """
        Wrapper around File.read() Reads n bytes starting from the current
        stream position.
        """
        return self._f.read(n)

    def _write(self, bs):
        """
        Wrapper around File.write(). Writes the data to the file which should
        be an iterable of bytes.
        """
        addr = self._f.write(bs)
        self._f.flush()
        return addr

    def _is_closed(self):
        return self._f.closed

    # internal utility methods
    def _zero_end(self):
        """
        Writes zero bytes at the end of the file so that reading a 0 integer at
        the end will succeed.
        """
        if self._is_empty() or self._seek_end() < self.INTEGER_LENGTH:
            self._seek_end()
            self._write_integer(0)
        else:
            self._seek(-self.INTEGER_LENGTH, os.SEEK_END)
            last_bytes = self._read(self.INTEGER_LENGTH)
            if any([byte != b'\x00' for byte in last_bytes]):
                self._seek_end()
                self._write_integer(0)

    def _read_integer(self):
        """Reads an integer from the file at the current stream position."""
        bs = self._read(self.INTEGER_LENGTH)
        return struct.unpack(self.INTEGER_FORMAT, bs)[0]  # struct.unpack always returns a tuple

    def _write_integer(self, n):
        """Writes an integer to the file at the current stream position."""
        bs = struct.pack(self.INTEGER_FORMAT, n)
        self._write(bs)

    def _read_integer_and_rewind(self):
        """
        Reads an integer from the file at the current stream position and
        leaves the current stream position unchanged.
        """
        n = self._read_integer()
        self._seek(-self.INTEGER_LENGTH, os.SEEK_CUR)
        return n

    def _write_formatted(self, data):
        """
        Writes an int with the length of the data followed by the data at the
        current stream position.
        """
        addr = self._tell()
        length = len(data) + self.INTEGER_LENGTH
        self._write_integer(length)
        self._write(data)
        return addr

    def _seek_formatted_data_end(self, start_at=0):
        """
        Moves the current stream position to the end of the data after start_at.

        Assumes that start_at is the starting position of formatted data ie that
        reading that address yields an integer with the length of the data that
        follows.
        """
        self._seek(start_at)
        length = self._read_integer_and_rewind()
        while length > 0:
            self._seek(length, os.SEEK_CUR)
            length = self._read_integer_and_rewind()

    # the external api
    def read(self, address):
        """
        Reads the data at the given address.

        Returns None if the address is past the end of the data on file.
        """
        self._seek(address)
        data_length = self._read_integer()
        if data_length == 0:
            return None
        data = self._read(data_length - self.INTEGER_LENGTH)
        return data

    def append(self, data):
        """
        Writes the data at the end of the file. Returns the address of the data
        in the file.
        """
        self._seek_formatted_data_end()
        last_address = self._write_formatted(data)
        self._zero_end()
        return last_address

    def close(self):
        self._f.close()

    @property
    def is_open(self):
        return not self.is_closed

    @property
    def is_closed(self):
        return self._is_closed()

    def next_address(self, address):
        """
        Returns the address of the first piece of data after address or None if
        there is no data past the address.
        """
        self._seek_start()
        length = self._read_integer_and_rewind()
        read_address = 0
        while read_address <= address and length > 0:
            length = self._read_integer_and_rewind()
            self._seek(length, os.SEEK_CUR)
            read_address += length
        if read_address == address:
            return None
        return read_address


# The logical layer
class Logical(object):
    def __init__(self, dbname):
        self._keys_storage = FileStorage(dbname + '.keys')
        self._values_storage = FileStorage(dbname + '.values')

    def _read_keys(self):
        keys = []
        address = 0
        while address is not None:
            key_data = self._keys_storage.read(address)
            if key_data is not None:
                key = pickle.loads(key_data)
                keys.append(key)
            address = self._keys_storage.next_address(address)
        return keys

    def _insert(self, key, value, for_deletion=False):
        if not for_deletion:
            value_data = pickle.dumps(value)
            value_address = self._values_storage.append(value_data)
        else:
            value_address = None
        key_tuple = (key, value_address)
        key_data = pickle.dumps(key_tuple)
        key_address = self._keys_storage.append(key_data)

    def get(self, key):
        # the key_data type is determined in _insert(), it's a tuple:
        # (key, value_address)
        # note that we do updates by inserting another copy of the key.
        # this means that to retrieve the key we have to look at all of them
        keys = self._read_keys()
        value_data = None
        for k, value_address in keys:
            if k == key:
                if value_address is None:
                    value_data = None
                else:
                    value_data = self._values_storage.read(value_address)
        if value_data is None:
            raise KeyError('Key %s not found' % key)
        return pickle.loads(value_data)

    def set(self, key, value):
        return self._insert(key, value, for_deletion=False)

    def pop(self, key):
        return self._insert(key, value=None, for_deletion=True)

    def close_storage(self):
        self._keys_storage.close()
        self._values_storage.close()



# The database API
class ScratchDB(object):
    pass


class QueryProcessor(object):
    pass


class Client(object):
    pass

