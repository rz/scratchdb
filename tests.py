import os
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


if __name__ == '__main__':
    unittest.main()
