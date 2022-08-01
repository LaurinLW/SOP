from typing import TextIO
import numpy as np
import os
import unittest

from django.forms import JSONField

from experiment.run.job import Job
from experiment.supply.job_generator import JobGenerator
from experiment.supply.parser.parameter_parser_json import JsonParameterParser
from experiment.supply.subspace.subspace import Subspace


class JobGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.np_array: np.dtype = np.array([[1, 2, 5], [10, 11, 14], [19, 20, 23]])
        self.models: list[str] = ["pyod.models.abod.ABOD", "pyod.models.anogan.AnoGAN"]
        self.np_array: np.ndarray = np.array([[1, 2, 5], [10, 11, 14], [19, 20, 23]])
        self.dimensions: list[str] = ["Eve", "Alice", "Bob"]
        self.subspace: Subspace = Subspace(self.np_array, self.dimensions)
        test_dir = (os.path.sep).join((__file__.split(".")[0]).split(os.path.sep)[0:-1])
        self.input_json_file: TextIO = open(os.path.join(test_dir, "test_resources", "job_generator_test_json.json"), "r")
        """self.input_json_file: JSONField = {
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
        }"""
        self.parser = JsonParameterParser(self.input_json_file)
        self.jobGenerator: JobGenerator = JobGenerator(
            self.models, self.parser
        )

    def test_generate_right_amount_jobs(self) -> None:
        self.assertTrue(2 == len(self.jobGenerator.generate(self.subspace)))

    def test_first_job_has_right_subspace_dimensions(self) -> None:
        list_jobs: list[Job] = self.jobGenerator.generate(self.subspace)
        print(list_jobs[0].get_subspace_data().shape)
        self.assertTrue(list_jobs[0].get_subspace_data().shape == (3, 3))
