import unittest
import datetime

from tbooks.logic import EuroPrice


class EuroPriceTestCase(unittest.TestCase):

	def test_GBP_value_of_EUR_1_on_18_08_2016_is_0_86073(self):

		self.assertEqual(EuroPrice.GetGBPValue(1, datetime.date(2016, 8, 18)), 0.86073)


if __name__ == '__main__':

	unittest.main()
