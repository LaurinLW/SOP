import unittest
import numpy as np

from experiment.supply.subspace.subspace import Subspace


class SubspaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.np_array: np.ndarray = np.array([[1, 2, 5], [10, 11, 14], [19, 20, 23]])
        self.dimensions: list[str] = ["Eve", "Alice", "Bob"]
        self.subspace: Subspace = Subspace(self.np_array, self.dimensions, np.ndarray([0, 1, 2]))

    def test_dimensions(self) -> None:
        self.assertTrue(self.dimensions == self.subspace.dimensions)

    def test_data(self) -> None:
        self.assertTrue(np.array_equal(self.np_array, self.subspace.data))
