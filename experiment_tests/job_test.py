import unittest
from experiment.run.job import Job
from experiment.supply.subspace.subspace import Subspace
from pyod.utils.data import generate_data
import numpy as np
from pyod.models.knn import KNN
from experiment.run.result import Result


class JobTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.data_shape = (10, 3)
        self.data, y = generate_data(
            train_only=True, n_train=self.data_shape[0], n_features=self.data_shape[1]
        )
        self.dimension_names = ["1", "2", "3"]
        self.parameters: dict = {
            "algorithm": "auto",
            "contamination": 0.1,
            "leaf_size": 30,
            "method": "largest",
            "metric": "minkowski",
            "metric_params": None,
            "n_jobs": 1,
            "n_neighbors": 5,
            "p": 2,
            "radius": 1.0,
        }
        self.subspace = Subspace(self.data, self.dimension_names, np.ndarray([0, 1, 2]))
        self.model = KNN()
        self.job = Job(subspace=self.subspace, klass=KNN(), parameters=self.parameters)
        self.untrained_job = Job(self.subspace, KNN())

    def test_get_outlier_score_untrained(self):
        self.assertTrue(self.untrained_job.get_outlier_scores() is None)

    def test_get_subspace_dim(self):
        dimensions = self.job.get_subspace_dimensions()
        for i, c in enumerate(self.dimension_names):
            self.assertEquals(c, dimensions[i])

    def test_get_subspace_data(self):
        self.assertTrue(np.array_equal(self.job.get_subspace_data(), self.data))

    def test_get_parameters(self):
        self.assertEqual(self.job.get_parameters(), self.model.get_params())
