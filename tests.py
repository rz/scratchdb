import os
import pickle
import unittest

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
        self.assertTrue(actual_content.startswith(content))

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

    def tearDown(self):
        self.instance.close_storage()
        self.delete_files()

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


if __name__ == '__main__':
    unittest.main()
