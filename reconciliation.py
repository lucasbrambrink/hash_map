import operator
from decimal import Decimal


class ReconciliationInputParser(object):
    D0_POS = 'D0-POS'
    D1_TRN = 'D1-TRN'
    D1_POS = 'D1-POS'

    def __init__(self, path=None):
        self.lines = None
        self.d0_position = []
        self.d1_trade = []
        self.d1_position = []
        POSITIONS = {
            self.D0_POS: self.d0_position,
            self.D1_TRN: self.d1_trade,
            self.D1_POS: self.d1_position
        }

        with open(path, 'r') as input_stream:
            lines = input_stream.read().splitlines()
            bucket = self.d0_position
            for line in lines[1:]:
                if not len(line):
                    continue

                if line in POSITIONS.keys():
                    bucket = POSITIONS[line]
                    continue

                bucket.append(line)



class Transaction(object):
    BUY = 'BUY'
    SELL = 'SELL'
    FEE = 'FEE'
    DEPOSIT = 'DEPOSIT'
    DIVIDEND = 'DIVIDEND'
    TRANSACTION_CODES = (
        BUY, SELL, FEE, DEPOSIT, DIVIDEND
    )


class PortfolioItem(object):

    def __init__(self, symbol, shares):
        self.symbol = symbol
        self.shares = Decimal(shares)

    def apply(self, transaction, shares):
        assert transaction in Transaction.TRANSACTION_CODES
        op = operator.sub if transaction == Transaction.SELL\
            else operator.add
        self.shares = op(self.shares, Decimal(shares))

    def __str__(self):
        return ' '.join((self.symbol, str(self.shares)))

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return self.shares + other.shares

    def __sub__(self, other):
        return PortfolioItem(symbol=self.symbol,
                             shares=self.shares - other.shares)

    def __ne__(self, other):
        return self.shares != other


class Cash(object):
    SYMBOL = 'Cash'

    def __init__(self, value):
        self.value = Decimal(value)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'Cash {}'.format(self.value)

    def apply(self, transaction, value):
        assert transaction in Transaction.TRANSACTION_CODES
        op = operator.add if transaction in (Transaction.SELL, Transaction.DIVIDEND, Transaction.DEPOSIT)\
            else operator.sub
        self.value = op(self.value, Decimal(value))

    def __sub__(self, other):
        assert type(other) is type(self)
        return Cash(value=self.value - other.value)

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other


class Portfolio(object):
    CASH = 'Cash'

    def __init__(self, items=None, cash=0, positions=None):
        self.items = items or {}
        self.cash = Cash(cash)
        if positions is not None:
            self.initialize_position(positions)

    def __repr__(self):
        return '[%s]' % ', '.join('{}: {}'.format(key, value.shares)
                                  for key, value in self.items.items())

    def trade(self, symbol, transaction_code, shares, value):
        if symbol == self.CASH:
            self.cash.apply(transaction_code, value)
        else:
            item = self.items.get(symbol) or PortfolioItem(symbol, 0)
            item.apply(transaction_code, shares)
            self.cash.apply(transaction_code, value)
            self.items[symbol] = item

    def initialize_position(self, positions):
        for position in positions:
            symbol, shares_or_value = position.split()
            if symbol == self.CASH:
                self.cash.apply(Transaction.DEPOSIT, shares_or_value)
            else:
                self.items[symbol] = PortfolioItem(symbol, shares_or_value)

    def __sub__(self, other):
        """establish the difference between 2 portfolios"""
        assert type(other) is type(self)
        diff = Portfolio()
        symbols = set(self.items.keys())
        symbols.update(other.items.keys())

        for symbol in symbols:
            self_position = self.items.get(symbol, PortfolioItem(symbol, 0))
            other_position = other.items.get(symbol, PortfolioItem(symbol, 0))
            diff.items[symbol] = self_position - other_position

        diff.cash = self.cash - other.cash
        return diff

    def __iter__(self):
        for key in sorted(self.items.keys()):
            yield self.items[key]



class OutputStream(object):
    DEFAULT = 'recon.out'

    def __init__(self, target=None):
        self.target = target or self.DEFAULT

    def __call__(self, stream, target=None):
        with open(self.target, 'w') as output:
            output.write(stream)
            output.write('\n')


class Reconciliation(object):
    DEFAULT_INPUT = 'recon.in'
    DEFAULT_OUTPUT = 'recon.out'

    def __init__(self, input_path=None, output_path=None):
        self.input_path = input_path or self.DEFAULT_INPUT
        self.output_path = output_path or self.DEFAULT_OUTPUT
        self.parser = ReconciliationInputParser(self.input_path)
        self.invalid = self.reconcile()
        self.write()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '\n'.join(self.invalid)

    def reconcile(self):
        portfolio = Portfolio(positions=self.parser.d0_position)
        for trade in self.parser.d1_trade:
            portfolio.trade(*trade.split())

        closing_portfolio = Portfolio(positions=self.parser.d1_position)
        reconciliation = closing_portfolio - portfolio

        invalid = []
        if self.fails_reconciliation(reconciliation.cash):
            invalid.append(str(reconciliation.cash))

        for position in reconciliation:
            if self.fails_reconciliation(position):
                invalid.append(str(position))

        return invalid

    def fails_reconciliation(self, value):
        return value != 0

    def write(self):
        output = OutputStream()
        output(str(self))




