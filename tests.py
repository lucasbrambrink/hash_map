from unittest import TestCase
from hash_map import HashMap, HashItem


class HashMapTestCase(TestCase):

    def setUp(self):
        self.hash_map = HashMap()

    def test__setitem__and__getitem__(self):
        self.hash_map['test'] = 'Test'
        self.assertEqual(self.hash_map['test'], 'Test')

    def test__set__duplicate(self):
        hash_map = HashMap()
        hash_map['new'] = 12
        self.assertEqual(hash_map['new'], 12)
        hash_map['new'] = 13
        self.assertEqual(hash_map['new'], 13)
        self.assertEqual(len(hash_map), 1)

    def test__contains__(self):
        self.hash_map['test'] = 'Test'
        self.assertIn('test', self.hash_map)
        self.assertNotIn('not_test', self.hash_map)
        self.assertRaises(KeyError, self.hash_map.__getitem__, 'not_test')

    def test_kwargs__init__(self):
        hash_map = HashMap(test="this")
        self.assertIn('test', hash_map)
        self.assertEqual(hash_map['test'], 'this')

    def test_index(self):
        self.assertEqual(self.hash_map.get_index('test'), 6)

    def test_len(self):
        hash_map = HashMap()
        self.assertEqual(len(hash_map), 0)
        hash_map['test'] = 'this'
        self.assertEqual(len(hash_map), 1)

    def test__delete__(self):
        hash_map = HashMap(test='this')
        self.assertEqual(len(hash_map), 1)
        del hash_map['test']
        self.assertEqual(len(hash_map), 0)

    def test__double__(self):
        hash_map = HashMap(test='this')
        self.assertEqual(hash_map.size, hash_map.NUM_SLOTS)
        hash_map.double()
        self.assertEqual(hash_map.size, hash_map.NUM_SLOTS * 2)
        hash_map.double()
        self.assertEqual(hash_map.size, hash_map.NUM_SLOTS * 4)

    def test__auto_double(self):
        """if reaches threshold, should scale up"""
        hash_map = HashMap()
        self.assertEqual(hash_map.size, hash_map.NUM_SLOTS)
        self.assertEqual(len(hash_map), 0)
        num_added = hash_map.NUM_SLOTS + 2
        for test in range(num_added):
            hash_map[str(test)] = test

        self.assertEqual(hash_map.size, hash_map.NUM_SLOTS * 2)
        self.assertEqual(len(hash_map), num_added)


class HashItemTestCase(TestCase):

    def setUp(self):
        self.item = HashItem('test', 'case')

    def test_key_value(self):
        item = HashItem('test', 'case')
        self.assertEqual(item.key, 'test')
        self.assertEqual(item.value, 'case')

    def test__eq__(self):
        item = HashItem('test', 'case')
        self.assertEqual(item, 'test')

    def test_hash(self):
        self.assertEqual(HashItem.hash('test'), 117021616)
        self.assertEqual(HashItem.hash('a'), 97)
        self.assertEqual(HashItem.hash('aa'), 9797)