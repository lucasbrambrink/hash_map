

class ReconciliationInputParser(object):
    """
    parses recon.in / stream of data
    """
    D0_POS = 'D0-POS'
    D1_TRN = 'D1-TRN'
    D1_POS = 'D1-POS'

    def __init__(self, path=None, stream=None):
        """reads path or stream"""
        assert bool(path) != bool(stream)  #xor
        self.lines = self.parse_lines(path, stream)
        self.d0_position = []
        self.d1_transactions = []
        self.d1_position = []
        self.parse_input()

    @staticmethod
    def parse_lines(path=None, stream=None):
        """read path or stream"""
        assert bool(path) != bool(stream)
        if path:
            with open(path, 'r') as input_stream:
                lines = input_stream.read().splitlines()
        else:
            lines = stream.splitlines()
        return lines

    def parse_input(self):
        assert self.lines[0] == self.D0_POS
        bucket = self.d0_position
        for line in self.lines[1:]:
            if not len(line):
                continue

            if line == self.D1_TRN:
                bucket = self.d1_transactions
                continue
            elif line == self.D1_POS:
                bucket = self.d1_position
                continue

            bucket.append(line)


class OutputStream(object):
    """handles output IO"""

    def __init__(self, target_path):
        self.target = target_path

    def __call__(self, stream, target=None):
        with open(self.target, 'w') as output:
            output.write(stream)
            output.write('\n')

