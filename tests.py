import os
import pickle
import unittest
from unittest import mock

import scratchdb


class FileStorageTest(unittest.TestCase):
    def setUp(self):
        self.filename = '__filestorage.test'
        self.delete_file()

    def tearDown(self):
        self.delete_file()

    def delete_file(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def test_init_creates(self):
        self.assertFalse(os.path.isfile(self.filename))
        fs = scratchdb.FileStorage(self.filename)
        self.assertTrue(os.path.isfile(self.filename))
        fs.close()

    def test_init_does_not_truncate(self):
        content = b'test\x00'
        with open(self.filename, 'bw') as f:
            f.write(content)
        fs = scratchdb.FileStorage(self.filename)
        fs.close()
        with open(self.filename, 'br') as f:
            actual_content = f.read()
        self.assertEqual(actual_content, content)

    def test_init_opens_file(self):
        fs = scratchdb.FileStorage(self.filename)
        self.assertFalse(fs._f.closed)
        fs.close()

    def test_close(self):
        fs = scratchdb.FileStorage(self.filename)
        fs.close()
        self.assertTrue(fs._f.closed)

    def test_init_zeroes_end(self):
        fs = scratchdb.FileStorage(self.filename)
        fs.close()
        with open(self.filename, 'br') as f:
            content = f.read()
        self.assertTrue(content.endswith(b'\x00'))

    def test_read(self):
        fs = scratchdb.FileStorage(self.filename)
        data = b'test value'
        address1 = fs.append(data)
        address2 = fs.append(data)
        self.assertEqual(data, fs.read(address1))
        self.assertEqual(data, fs.read(address2))
        fs.close()

    def test_append(self):
        fs = scratchdb.FileStorage(self.filename)
        data = b'test value'
        address = fs.append(data)
        self.assertEqual(0, address)
        address = fs.append(data)
        self.assertEqual(len(data) + fs.INTEGER_LENGTH, address)
        fs.close()
        with open(self.filename, 'br') as f:
            content = f.read()
        self.assertEqual(2, content.count(data))


class LogicalTest(unittest.TestCase):
    def setUp(self):
        self.dbname = '__testdb'
        self.delete_files()
        self.instance = scratchdb.Logical(self.dbname)

    def delete_files(self):
        for ext in ['.keys', '.values']:
            filename = self.dbname + ext
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    def test_init_opens_storage(self):
        keys_storage = self.instance._keys_storage
        values_storage = self.instance._values_storage
        self.assertTrue(keys_storage.is_open)
        self.assertTrue(values_storage.is_open)

    def test_close_storage(self):
        keys_storage = self.instance._keys_storage
        values_storage = self.instance._values_storage
        self.instance.close_storage()
        self.assertFalse(keys_storage.is_open)
        self.assertFalse(values_storage.is_open)

    def test_set(self):
        self.instance.set('testkey', 'testvalue')
        # the storage should be empty before we start, so both the key and the
        # value should be at address 0 of their respective storage
        expected_key_bytes = pickle.dumps(('testkey', 0))
        expected_value_bytes = pickle.dumps('testvalue')
        actual_key_bytes = self.instance._keys_storage.read(0)
        actual_value_bytes = self.instance._values_storage.read(0)
        self.assertEqual(expected_key_bytes, actual_key_bytes)
        self.assertEqual(expected_value_bytes, actual_value_bytes)

    def test_pop(self):
        self.instance.pop('testkey')
        # the storage should be empty before we start, so both the key and the
        # value should be at address 0 of their respective storage
        expected_key_bytes = pickle.dumps(('testkey', None))
        actual_key_bytes = self.instance._keys_storage.read(0)
        self.assertEqual(expected_key_bytes, actual_key_bytes)
        self.assertIsNone(self.instance._values_storage.read(0))

    def test_get(self):
        self.instance.set('testkey', 'testvalue')
        actual_value = self.instance.get('testkey')
        self.assertEqual('testvalue', actual_value)

    def test_get_non_existent(self):
        with self.assertRaises(KeyError):
            self.instance.get('testkey')

    def test_multi_set_get_pop(self):
        expected = {
            'key1': 'val1',
            'key2': 'val2',
            'foo': 3,
            'fool': 4,
            'fools': 5,
            'dict': {1:10, 2:20, 3:30},
            'list': [1, 2, 3],
            (1, 3): 'foo',
            (1, 4): 'fool',
            (1, 5): 'fools',
        }
        for key, val in expected.items():
            self.instance.set(key, val)

        with self.assertRaises(KeyError):
            self.instance.get('not-there')

        for key, expected_value in expected.items():
            self.assertEqual(expected_value, self.instance.get(key))

        self.instance.set('foo', 30)
        self.instance.pop('fool')

        self.assertEqual(30, self.instance.get('foo'))
        with self.assertRaises(KeyError):
            self.instance.get('fool')

        expected['foo'] = 30
        expected.pop('fool')
        for key, expected_value in expected.items():
            self.assertEqual(expected_value, self.instance.get(key))

    def tearDown(self):
        self.instance.close_storage()
        self.delete_files()


class ScratchDBAPITest(unittest.TestCase):
    def setUp(self):
        self.dbname = '__testdb'
        self.delete_files()
        self.db = scratchdb.ScratchDB(self.dbname)

    def delete_files(self):
        for ext in ['.keys', '.values']:
            filename = self.dbname + ext
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    def test_set_get(self):
        key = (1, 10)
        value = {'name': 'John Jones', 'age': 35}
        self.db.set(key, value)
        self.assertEqual(self.db.get(key), value)

    def test_get_nonexistent(self):
        with self.assertRaises(KeyError):
            self.db.get('nonexistentkey')

    def test_set_pop(self):
        key = (1, 10)
        value = 'John Jones is 35 years old.'
        self.db.set(key, value)

        self.db.pop(key)
        with self.assertRaises(KeyError):
            self.db.get(key)

    def tearDown(self):
        self.db.close()
        self.delete_files()


class QueryProcessorTest(unittest.TestCase):
    def setUp(self):
        self.dbname = '__testdb'
        self.delete_files()
        self.db = scratchdb.ScratchDB(self.dbname)
        self.qp = scratchdb.QueryProcessor(self.db)

    def delete_files(self):
        for ext in ['.keys', '.values']:
            filename = self.dbname + ext
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    def test_invalid_comand(self):
        cmd_str = 'not (1,"bit") {"valid":False}'
        actual = self.qp.execute(cmd_str)
        self.assertTrue(actual.startswith('Invalid query.'))

    def test_get_valid(self):
        key = (1, 10)
        value = [1, 2, 3]
        self.db.set(key, value)

        cmd_str = 'get (1,10)'
        actual = self.qp.execute(cmd_str)
        expected = '<list>: [1, 2, 3]'
        self.assertEqual(actual, expected)

    def test_get_valid_nonexistent(self):
        cmd_str = 'get nonexistent'
        actual = self.qp.execute(cmd_str)
        self.assertTrue(actual.startswith('Key not found'))

    def test_get_invalid_extra_args(self):
        cmd_str = 'get foo bar'
        actual = self.qp.execute(cmd_str)
        self.assertTrue(actual.startswith('Invalid query. get should only have one argument'))

    def tearDown(self):
        self.db.close()
        self.delete_files()


if __name__ == '__main__':
    unittest.main()
