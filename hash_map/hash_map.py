from utils import KeyValuePair, HashFunction


class HashMap(object):
    """
    1. hash key (str) into integer
        base-len(alphabet) => Python built-in printable characters: len == 100

    2. take hash mod len(array) => index (remainder is within range of array)

    3. store value in array at index
        leverage O(1) lookup on arrays

    4. implement sequential probing
        - if hash collision occurs, simply store in adjacent cell
        - w each lookup, check if key matches, else check adjacent cell
        - worsens lookup by O(n + m) where m is

    5. double size if hash map becomes full
    """

    NUM_SLOTS = 127  # 2^7-1
    BUFFER = 5  # threshold to double size of array
    HASH_FUNCTION = HashFunction.base_alphabet

    def get_index(self, key):
        index = self.HASH_FUNCTION(key) % self.size
        while self.array[index] is not None:
            # amortized lookup (not quite O(1))
            if self.array[index].key == key:
                break

            index = self.increment_index(index)

        return index

    def increment_index(self, index):
        """sequential probing: cycles index within bounds of array"""
        index += 1
        if index >= self.size:
            index = 0
        return index

    def __init__(self, **kwargs):
        """init empty array with null values w length(SIZE)"""
        self.size = self.NUM_SLOTS
        self.array = [None for x in range(self.size)]
        for key in kwargs:
            self.__setitem__(key, kwargs[key])

    def __setitem__(self, key, value):
        """implements sequential probing"""
        item = KeyValuePair(key, value)
        index = self.get_index(item.key)
        self.array[index] = item

        # double array size if hash_map becomes full
        if len(self) + self.BUFFER >= self.size:
            self.double()

    def __getitem__(self, item):
        """implement sequential probing"""
        index = self.get_index(item)
        stored_item = self.array[index]

        if stored_item is None:
            raise KeyError(item)

        return stored_item.value

    def __contains__(self, item):
        try:
            return self[item] is not None
        except KeyError:
            return False

    def __iter__(self):
        """iterate through keys only"""
        for item in filter(None, self.array):
            yield item.key

    def __delitem__(self, key):
        """because of sequential probing, we have to re-insert all hash-values"""
        index = self.get_index(key)
        self.array[index] = None
        for item in filter(None, self.array):
            self[item.key] = item.value

    def __repr__(self):
        """we can also use curly brackets"""
        return '{%s}' % ', '.join(
            '"{}": {}'.format(key, self[key])
            for key in self)

    def __len__(self):
        return self.size - self.array.count(None)

    def double(self):
        """double array size to make more space"""
        new_hash_map = HashMap()
        new_hash_map.size = self.size * 2
        new_hash_map.array = [None for x in range(new_hash_map.size)]
        for item in self:
            new_hash_map[item] = self[item]

        self.array = new_hash_map.array
        self.size = new_hash_map.size
