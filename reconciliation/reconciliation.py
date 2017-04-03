import os
import sys
from portfolio import Portfolio
from parser import ReconciliationInputParser, OutputStream


class Reconciliation(object):
    """
    class to delegate difference
    between 2 portfolios
    """
    DEFAULT_INPUT = 'recon.in'
    DEFAULT_OUTPUT = 'recon.out'

    def __init__(self, input_path=None, output_path=None):
        self.input_path = input_path or self.DEFAULT_INPUT
        self.output_path = output_path or self.DEFAULT_OUTPUT
        self.parser = ReconciliationInputParser(self.input_path)
        self.output = OutputStream(self.output_path)
        self.reconciled_portfolio = None
        self.invalid_positions = []

    def __call__(self, write=False):
        self.reconcile()
        if write:
            self.write()

    def reconcile(self):
        """
        1. initialize portfolio from Day-0 position
        2. take portfolio through day trades
        3. compare to reported portfolio position
        """
        portfolio = Portfolio(positions=self.parser.d0_position)
        for trade in self.parser.d1_transactions:
            portfolio.trade(*trade.split())

        closing_portfolio = Portfolio(positions=self.parser.d1_position)
        self.reconciled_portfolio = closing_portfolio - portfolio
        self.process_invalid_positions()

    def process_invalid_positions(self):
        """aggregate all failing reports"""
        assert self.reconciled_portfolio is not None
        self.invalid_positions = []
        if self.fails_reconciliation(self.reconciled_portfolio.cash):
            self.invalid_positions.append(str(self.reconciled_portfolio.cash))

        for position in self.reconciled_portfolio:
            if self.fails_reconciliation(position):
                self.invalid_positions.append(str(position))

    def fails_reconciliation(self, value):
        """reported position does not match transaction history
           i.e. non-zero value
        """
        return value != 0

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        """show reconciliation failures"""
        return '\n'.join(self.invalid_positions)

    def write(self):
        assert self.reconciled_portfolio is not None
        self.output(str(self))


if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = None if not len(sys.argv) > 2 else sys.argv[2]
    if not input_file or not os.path.isfile(input_file):
        raise IOError('Must point to valid input file')

    reconcile = Reconciliation(input_path=input_file,
                               output_path=output_file)
    reconcile(write=True)
