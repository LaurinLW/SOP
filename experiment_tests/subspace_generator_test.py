from cmath import nan
import numpy as np
import pandas as pd
import unittest

from pandas import DataFrame

from experiment.supply.subspace.subspace import Subspace
from experiment.supply.subspace.subspace_generator import SubspaceGenerator
from experiment.supply.preprocessing.cleaner import Cleaner
from experiment.supply.preprocessing.cleaner_drop_nan import DropNaNCleaner
from experiment.supply.preprocessing.encoder import Encoder
from experiment.supply.preprocessing.encoder_one_hot import EncoderOneHot


class SubspaceGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.counter: int = 0
        self.number_subspaces: int = 5
        self.min_dimension: int = 3
        self.max_dimension: int = 6
        self.starting_seed: int = 1234
        self.data: DataFrame = pd.DataFrame(
            np.array(
                [
                    [1, 2, 3, 4, 5, 6, 7, 8, 9],
                    [nan, 11, 12, 13, 14, 15, 16, 17, 18],
                    [19, 20, 21, 22, 23, 24, 25, 26, 27],
                ]
            ),
            columns=["a", "b", "c", "d", "e", "f", "g", "h", "i"],
        )
        self.cleaner: Cleaner = DropNaNCleaner()
        self.encoder: Encoder = EncoderOneHot()

        self.subspace_generator: SubspaceGenerator = SubspaceGenerator(
            self.number_subspaces,
            self.min_dimension,
            self.max_dimension,
            self.starting_seed,
            self.data,
            self.encoder,
            self.cleaner,
        )
        self.test_subspace_list: list[Subspace] = list()
        self.iterator = iter(self.subspace_generator)

        while True:
            try:
                subspace = next(self.iterator)

            except StopIteration:
                break
            else:
                self.test_subspace_list.append(subspace)

    def test_correct_number_of_subspaces_created(self) -> None:
        self.assertTrue(len(self.test_subspace_list) == self.number_subspaces)

    def test_amount_columns_equals_amount_dimension_names_if_no_categorical(
        self,
    ) -> None:
        self.assertTrue(
            len(self.test_subspace_list[0].dimensions)
            == np.size(self.test_subspace_list[0].data, 1)
        )
