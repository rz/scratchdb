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

    def _get_head_node(self):
        head_address = self._storage.get_head_address()
        if head_address == 0:
            head = None
        else:
            head = self._storage.read(head_address)
        return head

    def _ll_insert(self, node, key, value_address):
        if node is None:
            # inserting on an empty list
            new_node = Node(key, value_address, None)
            new_node_address = self._storage.append(new_node)
            return new_node_address

        if key == node.key:
            # we are updating an existing key
            # make a new node with value_address and next_address pointing to
            # the existing next node i.e. we can re-use the rest of the list
            new_node = Node(key, value_address, node.next_address)
            new_node_address = self._storage.append(new_node)
            return new_node_address
        else:
            if node.next_address is None:
                # got to the end without finding the key i.e. it's a new key
                # first, make a new node with the value_address to serve as the
                # new last node i.e. its next_address is None
                new_last_node = Node(key, value_address, None)
                new_last_node_address = self._storage.append(new_last_node)
                # then, copy of the current node (the former last node) but
                # point its next_address to the new last-node we just created
                new_existing_node = Node(node.key, node.value_address, new_last_node_address)
                new_existing_node_address = self._storage.append(new_existing_node)
                return new_existing_node_address
            else:
                # recursive case
                # we are not at the end and we haven't found the key, yet
                # copy this node as is but point its next address to the return
                # value of calling _ll_insert() with the next node
                next_node = self._storage.read(node.next_address)
                new_next_node_address = self._ll_insert(next_node, key, value_address)
                new_node = Node(node.key, node.value_address, new_next_node_address)
                new_node_address = self._storage.append(new_node)
                return new_node_address

    def get(self, key):
        pass

    def set(self, key, value):
        vw = ValueWrapper(value)
        value_address = self._storage.append(vw)
        head = self._get_head_node()
        new_head_address = self._ll_insert(head, key, value_address)
        self._storage.set_head_address(new_head_address)
        return new_head_address

    def pop(self, key):
        pass

    def show(self):
        result_str = ''
        node = self._get_head_node()
        while node is not None:
            if node.value_address is None:
                value = None
            else:
                value = self._storage.read(node.value_address)
            result_str += '[%s value_addr:%s]-->' % (node.key, node.value_address)
            if node.next_address is None:
                node = None
            else:
                node = self._storage.read(node.next_address)
        print('list: %s' % result_str)
        print('head address: %s' % self._storage.get_head_address())
        print('storage:')
        self._storage.show()


if __name__ == '__main__':
    ll = LogicalLinkedList()
    print('inserting 5 keys: k0,k1,k2,k3,k4')
    for i in range(5):
        ll.set('k%s' %i, 'v%s' % i)
        ll.show()
    print('updating k2 to new v2')
    ll.set('k2', 'new v2')
    ll.show()

