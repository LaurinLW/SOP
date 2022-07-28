import unittest
import numpy as np

from django.forms import JSONField
from multiprocessing import Queue
from pandas import DataFrame
from threading import Event


class JobSupplierTest(unittest.TestCase):
    def setUp(self):
        self.number_subspaces: int = 4
        self.min_dimension: int = 5
        self.max_dimension: int = 10
        self.seed: int = 42
        self.data: DataFrame = DataFrame(
            np.array(
                [
                    [1, "Deutschland", 3, 4, 5, 6, 7, 8, 9],
                    [10, "Österreich", 12, 13, 14, 15, 16, 17, 18],
                    [19, "Schweiz", 21, 22, 23, 24, 25, 26, 27],
                ]
            ),
            columns=["a", "Land", "c", "d", "e", "f", "g", "h", "i"],
        )
        self.models: list[str] = ["pyod.models.abod.ABOD", "pyod.models.anogan.AnoGAN"]
        self.parameters: JSONField = {
            "pyod.models.abod.ABOD": {
                "contamination": 0.2,
                "n_neighbors": 9,
                "method": "fast",
            },
            "pyod.models.anogan.AnoGAN": {
                "activation_hidden": "tanh",
                "dropout_rate": 0.3,
                "latent_dim_G": 2,
                "G_layers": [20, 10, 3, 10, 20],
                "verbose": 1,
                "D_layers": [20, 10, 5],
                "index_D_layer_for_recon_error": 1,
                "epochs": 400,
                "preprocessing": True,
                "learning_rate": 0.005,
                "learning_rate_query": 0.001,
                "epochs_query": 20,
                "index_D_layer_for_recon_error": 1,
                "batch_size": 30,
                "output_activation": None,
                "contamination": 0.1,
            },
        }
        self.out: Queue = Queue(8)
        self.stop: Event = Event()
