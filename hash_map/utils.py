import string
from hashlib import sha256


class HashFunction(object):
    ALPHABET = string.printable
    RANGE = len(ALPHABET)

    @classmethod
    def base_alphabet(cls, value):
        """create int of base-N (num symbols, i.e. length of alphabet)"""
        assert type(value) is str
        key_length = len(value)
        return sum(
            cls.RANGE ** (key_length - (x + 1)) * ord(value[x])
            for x in range(key_length)
        )

    @classmethod
    def sha256(cls, value):
        """cast sha256 to int"""
        assert type(value) is str
        return int(sha256(value.encode()).hexdigest(), 16)


class KeyValuePair(object):
    """ simple key-value pair """

    def __init__(self, key, value):
        for c in key:
            assert c in HashFunction.ALPHABET

        self.key = key
        self.value = value

    def __eq__(self, other):
        return self.key == other
