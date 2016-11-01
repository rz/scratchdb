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
            new_node = ('key', key, value_address, None)
            new_node_address = self._storage.append(new_node)
            return new_node_address

        _, node_key, node_value_address, next_node_address = node
        if key == node_key:
            # we are updating an existing key
            # make a new node with value_address and next_address pointing to
            # the existing next node i.e. we can re-use the rest of the list
            new_node = ('key', key, value_address, next_node_address)
            new_node_address = self._storage.append(new_node)
            return new_node_address
        else:
            if next_node_address is None:
                # got to the end without finding the key i.e. it's a new key
                # first, make a new node with the value_address to serve as the
                # new last node i.e. its next_address is None
                new_last_node = ('key', key, value_address, None)
                new_last_node_address = self._storage.append(new_last_node)
                # then, copy of the current node (the former last node) but
                # point its next_address to the new last-node we just created
                new_existing_node = ('key', node_key, node_value_address, new_last_node_address)
                new_existing_node_address = self._storage.append(new_existing_node)
                return new_existing_node_address
            else:
                # recursive case
                # we are not at the end and we haven't found the key, yet
                # copy this node as is but point its next address to the return
                # value of calling _ll_insert() with the next node
                next_node = self._storage.read(next_node_address)
                new_next_node_address = self._ll_insert(next_node, key, value_address)
                new_node = ('key', node_key, node_value_address, new_next_node_address)
                new_node_address = self._storage.append(new_node)
                return new_node_address

    def _ll_remove(self, node, key):
        if node is None:
            # removing from an empty list, nothing to do
            return 0
        _, node_key, node_value_address, node_next_address = node
        if node_next_address is None:
            next_node = None
        else:
            next_node = self._storage.read(node_next_address)

        if next_node is None:
            if key == node_key:
                # there is only 1 node and it is the one we need to remove
                # we know there's only 1 node because this method operates
                # by removing the next node, so we can only get here if
                # next_node was None on the first call
                return 0
            else:
                # we make a copy for uniformity and because we need to return
                # the address of this node. if we had the address of this node
                # we could just return that and in that case, when removing
                # a non-existent key all but the last node would be copied
                # this copies the last node
                new_node = ('key', node_key, node_value_address, node_next_address)
                new_node_address = self._storage.append(new_node)
                return new_node_address
        _, next_node_key, next_node_value_address, next_node_next_address = next_node
        if key == next_node_key:
            # the node we need to remove is next
            new_node = ('key', node_key, node_value_address, next_node_next_address)
            new_node_address = self._storage.append(new_node)
            return new_node_address
        else:
            # recursive case, make a copy of the present node and recurse
            new_next_node_address = self._ll_remove(next_node, key)
            new_node = ('key', node_key, node_value_address, new_next_node_address)
            new_node_address = self._storage.append(new_node)
            return new_node_address

    def _insert(self, key, value):
        value_tuple = ('value', value)  # so that it is easy to identify them when inspecting the storage
        value_address = self._storage.append(value_tuple)
        head_address = self._storage.get_head_address()
        head = self._get_head_node()
        new_head_address = self._ll_insert(head, key, value_address)
        self._storage.set_head_address(new_head_address)
        return new_head_address

    def _remove(self, key):
        head_address = self._storage.get_head_address()
        head = self._get_head_node()
        new_head_address = self._ll_remove(head, key)
        self._storage.set_head_address(new_head_address)
        return new_head_address

    def get(self, key):
        node = self._get_head_node()
        while node is not None:
            _, node_key, value_address, next_address = node
            if node_key == key:
                if value_address is None:
                    raise KeyError('Not found: %s' % key)
                _, value = self._storage.read(value_address)
                return value
            node = self._storage.read(next_address)
        raise KeyError('Not found: %s' % key)

    def set(self, key, value):
        return self._insert(key, value)

    def pop(self, key):
        return self._remove(key)

    def show(self):
        result_str = ''
        node = self._get_head_node()
        while node is not None:
            _, key, value_address, next_address = node
            if value_address is None:
                value = None
            else:
                value = self._storage.read(value_address)
            result_str += '[%s value_addr:%s]-->' % (key, value_address)
            if next_address is None:
                node = None
            else:
                node = self._storage.read(next_address)
        print('list: %s' % result_str)
        print('head address: %s' % self._storage.get_head_address())
        print('storage:')
        self._storage.show()

