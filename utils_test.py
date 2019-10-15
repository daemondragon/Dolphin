import unittest
import numpy as np

class IdConversionTest(unittest.TestCase):

    def test_round(self):
        # Check that the conversion can be done in both way
        # without failing
        id_list = [x * 2 for x in range(2, 30)] # TODO: get the real ids
        converved_list = id_list # TODO: do idToIndex conversion
        new_id_list = converved_list # TODO: doIndexToId conversion

        self.assertEqual(id_list, new_id_list)

    def test_id_to_index(self):
        id_list = [x * 2 for x in range(2, 30)]

        converved_list = id_list # TODO: do idToIndex conversion

        # Same len
        self.assertEqual(len(id_list), len(converved_list))
        # Correct content
        self.assertEqual(converved_list, list(range(len(id_list))))

class ConstraintsTests(unittest.TestCase):

    def test_assets_ratio(self):
        for (scenario, result) in [# TODO: get portfolio
            ([], True),
            ([], False),
        ]:
            ratio_asset = 0.6 # TODO: get ratio from scenario
            self.assertEqual(ratio_asset >= 0.5, result)

    def test_amount(self):
        for (amount, result) in [
            (10, False),# Less than 15 asset
            (60, False),# More than 40 asset, with correct percent
            (34, True),# Correct number of assets
        ]:
            portfolio = np.block([np.full((amount,), 1 / amount), np.zeros((400-amount,))])

            self.assertEqual(result, result) # TODO: compute validity of the portfolio

    def test_weight_ratio(self):
        for (amount, result) in [
            (5, False),# Above 10% (20%)
            (120, False),# Under 1%
            (34, True),# Correct weight range
        ]:
            portfolio = np.full((amount,), 1 / amount)
            self.assertEqual(result, result) # TODO: compute validity of the portfolio


    def test_sum(self):
        # Check that the sum is always 1 (not an invalid portfolio)
        for (amount, result) in [
            (0.99, False),
            (1.01, False),
            (1.00, True),
        ]:
            portfolio = np.full((30,), 1 / amount)
            self.assertEqual(result, result) # TODO: compute validity of the portfolio

if __name__ == '__main__':
    unittest.main()