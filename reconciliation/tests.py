from unittest import TestCase
from parser import ReconciliationInputParser, OutputStream
from portfolio import Portfolio, PortfolioItem, Cash, Transaction
from reconciliation import Reconciliation
from decimal import Decimal
import os


class PortfolioItemTestCase(TestCase):

    def setUp(self):
        self.portfolio = Portfolio()

    def test_attributes(self):
        item = PortfolioItem('TEST', 1000)
        self.assertEqual(item.symbol, 'TEST')
        self.assertEqual(item.shares, 1000)

    def test__repr__(self):
        item = PortfolioItem('TEST', 1000)
        self.assertEqual(str(item), 'TEST 1000')


class CashTestCase(TestCase):

    def test__repr__(self):
        item = Cash(1000)
        self.assertEqual(str(item), 'Cash 1000')

    def test__sub__(self):
        diff = Cash(300) - Cash(100)
        self.assertEqual(diff.value, 200)

    def test__eq__(self):
        equal = Cash(100) == Cash(100)
        self.assertTrue(equal)


class PortfolioTestCase(TestCase):

    def test__contains__(self):
        portfolio = Portfolio(positions=["TEST 100"])
        self.assertIn("TEST", portfolio)

    def test__position(self):
        portfolio = Portfolio(positions=["TEST 100", "Cash 123.12"])
        self.assertEqual(portfolio.cash.value, Decimal('123.12'))
        self.assertIn("TEST", portfolio.items)
        self.assertEqual(portfolio.items["TEST"].symbol, "TEST")
        self.assertEqual(portfolio.items["TEST"].shares, 100)

    def test__sub__(self):
        portfolio1 = Portfolio(positions=["TEST 100", "Cash 200"])
        portfolio2 = Portfolio(positions=["TEST 130", "GOOG 120", "Cash 100"])
        diff = portfolio2 - portfolio1
        self.assertIn("TEST", diff)
        self.assertIn("GOOG", diff)
        self.assertEqual(diff.items["TEST"].shares, Decimal(30))
        self.assertEqual(diff.items["GOOG"].shares, Decimal(120))
        self.assertEqual(diff.cash, Decimal(-100))

    def test__trade(self):
        portfolio = Portfolio(positions=["TEST 100", "Cash 123.12"])
        portfolio.trade('TEST', Transaction.SELL, 50, 200)
        self.assertEqual(portfolio.cash.value, Decimal('323.12'))
        self.assertIn('TEST', portfolio)
        self.assertEqual(portfolio.items['TEST'].shares, Decimal(50))


class TransactionTestCase(TestCase):

    def test_transaction_buy(self):
        """item should have appropriate #shares and cash should be deducted from portfolio"""
        portfolio = Portfolio(cash=1000)
        transaction = Transaction(portfolio)
        item = transaction('TEST', Transaction.BUY, 10, 1000)
        self.assertIsNotNone(item)
        self.assertEqual(item.shares, 10)
        self.assertEqual(portfolio.cash.value, 0)

    def test_transaction_sell(self):
        """item should have appropriate #shares and cash should be added from portfolio"""
        portfolio = Portfolio(cash=1000)
        transaction = Transaction(portfolio)
        item = transaction('TEST', Transaction.SELL, 10, 1000)
        self.assertIsNotNone(item)
        self.assertEqual(item.shares, -10)
        self.assertEqual(portfolio.cash.value, 2000)

    def test_transaction_dividend(self):
        """item should be none and cash should be added from portfolio"""
        portfolio = Portfolio(cash=1000)
        transaction = Transaction(portfolio)
        item = transaction('TEST', Transaction.DIVIDEND, 0, 1000)
        self.assertIsNone(item)
        self.assertEqual(portfolio.cash.value, 2000)

    def test_transaction_fee(self):
        """item should be none and cash should be deducted from portfolio"""
        portfolio = Portfolio(cash=1000)
        transaction = Transaction(portfolio)
        item = transaction('TEST', Transaction.FEE, 0, 1000)
        self.assertIsNone(item)
        self.assertEqual(portfolio.cash.value, 0)

    def test_transaction_deposit(self):
        """item should be none and cash added to portfolio"""
        portfolio = Portfolio(cash=1000)
        transaction = Transaction(portfolio)
        item = transaction('TEST', Transaction.DEPOSIT, 0, 1000)
        self.assertIsNone(item)
        self.assertEqual(portfolio.cash.value, 2000)


class FixtureIOTestCase(TestCase):
    """
    abstract class to handle setUp & tearDown for recon.in
        - write value to tmp file to test IO
    """
    TEST_PATH = 'test_recon.in'
    D0_POS = 'D0-POS\nTEST 100\nCash 123.12\n'
    D1_TRN = 'D1-TRN\nTEST SELL 50 1000\n'
    D1_POS = 'D1-POS\nTEST 200\nCash 223.12\n'
    # mismatch of Cash -900, TEST 150
    TEST_INPUT = '%s%s%s' % (D0_POS, D1_TRN, D1_POS)

    def setUp(self):
        with open(self.TEST_PATH, 'w') as test_file:
            test_file.write(self.TEST_INPUT)
            test_file.flush()

    def tearDown(self):
        os.remove(self.TEST_PATH)


class InputParserTestCase(FixtureIOTestCase):

    def test_parser_day_0_position(self):
        parser = ReconciliationInputParser(self.TEST_PATH)
        self.assertEqual(len(parser.d0_position), 2)
        self.assertIn('TEST 100', parser.d0_position)
        self.assertIn('Cash 123.12', parser.d0_position)

    def test_parser_day_1_position(self):
        parser = ReconciliationInputParser(self.TEST_PATH)
        self.assertEqual(len(parser.d1_position), 2)
        self.assertIn('TEST 200', parser.d1_position)
        self.assertIn('Cash 223.12', parser.d1_position)

    def test_parser_day_1_transactions(self):
        parser = ReconciliationInputParser(self.TEST_PATH)
        self.assertEqual(len(parser.d1_transactions), 1)
        self.assertIn('TEST SELL 50 1000', parser.d1_transactions)


class OutputStreamTest(TestCase):
    OUTPUT_PATH = 'test.out'
    TEST_STREAM = "TEST"

    def setUp(self):
        if os.path.isfile(self.OUTPUT_PATH):
            os.remove(self.OUTPUT_PATH)

    def test_write_stream(self):
        output = OutputStream(self.OUTPUT_PATH)
        self.assertFalse(os.path.isfile(self.OUTPUT_PATH))
        output(self.TEST_STREAM)
        self.assertTrue(os.path.isfile(self.OUTPUT_PATH))

        with open(self.OUTPUT_PATH, 'r') as test:
            self.assertEqual(self.TEST_STREAM + '\n', test.read())

        os.remove(self.OUTPUT_PATH)


class ReconciliationTestCase(FixtureIOTestCase):
    OUTPUT_PATH = 'test.out'

    def setUp(self):
        super(ReconciliationTestCase, self).setUp()
        if os.path.isfile(self.OUTPUT_PATH):
            os.remove(self.OUTPUT_PATH)

    def test_reconciliation(self):
        """reconciliation should fail for TEST by 150, Cash -900"""
        reconcile = Reconciliation(input_path=self.TEST_PATH)
        reconcile()
        self.assertIn('TEST 150', reconcile.invalid_positions)
        self.assertIn('Cash -900.00', reconcile.invalid_positions)

    def test_write(self):
        """ensure writing IO creates file"""
        reconcile = Reconciliation(input_path=self.TEST_PATH,
                                   output_path=self.OUTPUT_PATH)
        self.assertFalse(os.path.isfile(self.OUTPUT_PATH))
        reconcile(write=True)
        self.assertTrue(os.path.isfile(self.OUTPUT_PATH))
        os.remove(self.OUTPUT_PATH)

    def test_output_content(self):
        """ensure output corresponds to failed items"""
        reconcile = Reconciliation(input_path=self.TEST_PATH,
                                   output_path=self.OUTPUT_PATH)
        self.assertFalse(os.path.isfile(self.OUTPUT_PATH))
        reconcile(write=True)
        with open(self.OUTPUT_PATH, 'r') as test_file:
            lines = test_file.read()
        self.assertEqual('Cash -900.00\nTEST 150\n', lines)
        os.remove(self.OUTPUT_PATH)


