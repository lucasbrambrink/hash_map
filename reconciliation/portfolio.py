from decimal import Decimal


class Transaction(object):
    BUY = 'BUY'
    SELL = 'SELL'
    FEE = 'FEE'
    DEPOSIT = 'DEPOSIT'
    DIVIDEND = 'DIVIDEND'
    TRANSACTION_CODES = (
        BUY, SELL, FEE, DEPOSIT, DIVIDEND
    )

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def __call__(self, symbol, transaction_code, shares, value):
        assert transaction_code in Transaction.TRANSACTION_CODES
        shares = Decimal(shares)
        value = Decimal(value)
        item = PortfolioItem(symbol, 0)
        if not symbol == self.portfolio.cash.SYMBOL:
            item = self.portfolio.items.get(symbol, item)

        if transaction_code == Transaction.SELL:
            item.shares -= shares
            self.portfolio.cash.value += value

        elif transaction_code == Transaction.BUY:
            item.shares += shares
            self.portfolio.cash.value -= value

        elif transaction_code in (Transaction.DEPOSIT, Transaction.DIVIDEND):
            self.portfolio.cash.value += value

        elif transaction_code == Transaction.FEE:
            self.portfolio.cash.value -= value

        return item if transaction_code in (Transaction.SELL, Transaction.BUY) \
            else None


class PortfolioItem(object):
    """ position in the account
    """

    def __init__(self, symbol, shares):
        self.symbol = symbol
        self.shares = Decimal(shares)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ' '.join((self.symbol, str(self.shares)))

    def __add__(self, other):
        return self.shares + other.shares

    def __sub__(self, other):
        """diff between two positions iff same symbol"""
        assert self.symbol == other.symbol
        return PortfolioItem(symbol=self.symbol,
                             shares=self.shares - other.shares)

    def __ne__(self, other):
        return self.shares != other


class Cash(object):
    SYMBOL = 'Cash'

    def __init__(self, value):
        self.value = Decimal(value)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '{} {}'.format(self.SYMBOL, self.value)

    def __sub__(self, other):
        assert type(other) is type(self)
        return Cash(value=self.value - other.value)

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other


class Portfolio(object):
    """
    maintains state of cash and collection of positions
    performs transaction
    """

    def __init__(self, items=None, cash=0, positions=None):
        self.items = items or {}
        self.cash = Cash(cash)
        if positions is not None:
            self.initialize_position(positions)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Portfolio: %s' % ', '.join('{}: {}'.format(key, value.shares)
                                  for key, value in self.items.items())

    def trade(self, symbol, transaction_code, shares, value):
        """apply transaction to cash and positions"""
        transaction = Transaction(portfolio=self)
        item = transaction(symbol, transaction_code, shares, value)
        if item is not None:
            self.items[symbol] = item

    def initialize_position(self, positions):
        """load cash and positions"""
        for position in positions:
            symbol, shares_or_value = position.split()
            if symbol == self.cash.SYMBOL:
                self.cash.value += Decimal(shares_or_value)
            else:
                self.items[symbol] = PortfolioItem(symbol, shares_or_value)

    def __sub__(self, other):
        """return the difference between self and another portfolio"""
        assert type(other) is type(self)
        diff = Portfolio()
        symbols = set(self.items.keys())
        symbols.update(other.items.keys())

        for symbol in symbols:
            self_position = self.items.get(symbol, PortfolioItem(symbol, 0))
            other_position = other.items.get(symbol, PortfolioItem(symbol, 0))
            # store diff of two items
            diff.items[symbol] = self_position - other_position

        diff.cash = self.cash - other.cash
        return diff

    def __iter__(self):
        """show positions in alphabetical order"""
        for key in sorted(self.items.keys()):
            yield self.items[key]

    def __contains__(self, item):
        return item in self.items.keys()

    def __getitem__(self, item):
        """implement sequential probing"""
        return self.items[item]