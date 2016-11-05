from collections import namedtuple


class MemoryStorage(object):
    def __init__(self):
        self._l = [0]

    def read(self, address):
        return self._l[address]

    def append(self, data):
        self._l.append(data)
        last_address = len(self._l) - 1
        return last_address

    def set_head_address(self, address):
        self._l[0] = address

    def get_head_address(self):
        return self._l[0]

    def show(self):
        header = 'addr   data'
        elements_s = '\n'.join('{:4d}   {}'.format(i, elem) for i, elem in enumerate(self._l))
        print(header)
        print(elements_s)


Node = namedtuple('Node', ['key', 'value_address', 'next_address'])


ValueWrapper = namedtuple('V', ['value'])


class LogicalLinkedList(object):
    def __init__(self):
        self._storage = MemoryStorage()

    def get(self, key):
        pass

    def set(self, key, value):
        pass

    def pop(self, key):
        pass

