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

    def test_set_data(self) -> None:
        old_data = self.subspace.data
        self.subspace.data = np.array([[1, 2, 6], [10, 11, 14], [19, 20, 23]])
        self.assertTrue(old_data is self.subspace.data)
    
    def test_set_dimensions(self) -> None:
        old_dimensions = self.subspace.dimensions
        self.subspace.dimensions = ["Eve", "Alice", "Max"]
        self.assertTrue(old_dimensions is self.subspace.dimensions)
