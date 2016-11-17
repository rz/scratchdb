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

    def _get_head(self):
        head_address = self._storage.get_head_address()
        if head_address == 0:
            head = None
            head_address = None
        else:
            head = self._storage.read(head_address)
        return head, head_address

    def _ll_contains(self, key):
        try:
            self.get(key)
        except KeyError:
            return False
        else:
            return True

    def _ll_insert(self, key, value_address):
        node, head_address = self._get_head()
        if not self._ll_contains(key):
            new_node = Node(key, value_address, next_address=head_address)
            new_head_address = self._storage.append(new_node)
            return new_head_address
        # we know that the list contains the key, so the break will terminate the loop
        to_copy = []
        while True:
            if key == node.key:
                new_node = Node(key, value_address, node.next_address)
                new_node_address = self._storage.append(new_node)
                break
            to_copy.append(node)
            node = self._storage.read(node.next_address)
        for n in reversed(to_copy):
            new_node = Node(n.key, n.value_address, next_address=new_node_address)
            new_node_address = self._storage.append(new_node)
        return new_node_address

    def get(self, key):
        node, _ = self._get_head()
        while node is not None:
            if key == node.key:
                vw = self._storage.read(node.value_address)
                return vw.value
            if node.next_address is None:
                node = None
            else:
                node = self._storage.read(node.next_address)
        raise KeyError('Not found: %s' % key)

    def set(self, key, value):
        vw = ValueWrapper(value)
        value_address = self._storage.append(vw)
        new_head_address = self._ll_insert(key, value_address)
        self._storage.set_head_address(new_head_address)
        return new_head_address

    def pop(self, key):
        pass

    def show(self):
        result_str = ''
        node, _ = self._get_head()
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
        print('-'*30)


if __name__ == '__main__':
    ll = LogicalLinkedList()
    print('inserting 5 keys: k0,k1,k2,k3,k4')
    for i in range(5):
        ll.set('k%s' %i, 'v%s' % i)
        ll.show()
    for i in range(5):
        print('get k%s:' % i, ll.get('k%s' % i))
    print('getting non-existent:', end=' ')
    try:
        ll.get('DNE')
    except KeyError as e:
        print('got KeyError', e, end='\n\n')

    print('updating k2 to new v2')
    ll.set('k2', 'new v2')
    ll.show()

    print('get k2:', ll.get('k2'))

