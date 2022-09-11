import numpy as np
import pandas as pd
import unittest

from experiment.supply.preprocessing.cleaner_drop_nan import DropNaNCleaner


class CleanerDropNanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dataFrame = pd.DataFrame(
            {"col1": [0, 1, 2, 3], "col2": pd.Series([2, 3], index=[2, 3])},
            index=[0, 1, 2, 3],
        )
        self.cleaner = DropNaNCleaner()
        self.solution = pd.DataFrame(
            {"col1": [2, 3], "col2": pd.Series([2, 3], index=[0, 1])}, index=[0, 1]
        )

    def test_clean_with_NaN(self) -> None:
        self.assertTrue(
            np.array_equal(
                self.solution.to_numpy(dtype=np.float32),
                self.cleaner.clean(self.dataFrame).to_numpy(dtype=np.float32),
            )
        )

    def test_clean_without_NaN(self) -> None:
        self.assertTrue(
            np.array_equal(
                self.solution.to_numpy(dtype=np.float32),
                self.cleaner.clean(self.solution).to_numpy(dtype=np.float32),
            )
        )
