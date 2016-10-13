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
        with open(self.filename, 'w') as f:
            f.write('test')
        fs = scratchdb.FileStorage(self.filename)
        fs.close()
        with open(self.filename) as f:
            contents = f.read()
        self.assertEqual(contents, 'test')

    def test_init_opens_file(self):
        fs = scratchdb.FileStorage(self.filename)
        self.assertFalse(fs._f.closed)
        fs.close()

    def test_close(self):
        fs = scratchdb.FileStorage(self.filename)
        fs.close()
        self.assertTrue(fs._f.closed)


if __name__ == '__main__':
    unittest.main()
