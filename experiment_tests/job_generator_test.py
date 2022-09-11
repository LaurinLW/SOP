from typing import TextIO
import numpy as np
import os
import unittest


from experiment.run.job import Job
from experiment.run.result import Result
from experiment.supply.job_generator import JobGenerator
from experiment.supply.parser.parameter_parser_json import JsonParameterParser
from experiment.supply.subspace.subspace import Subspace


class JobGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.np_array: np.ndarray = np.array([[1, 2, 5], [10, 11, 14], [19, 20, 23]])
        self.models: list[str] = ["pyod.models.abod.ABOD", "pyod.models.anogan.AnoGAN"]
        self.models_exception: list[str] = ["test"]
        self.dimensions: list[str] = ["Eve", "Alice", "Bob"]
        self.subspace: Subspace = Subspace(
            self.np_array, self.dimensions, np.ndarray([0, 1, 2])
        )
        test_dir = (os.path.sep).join((__file__.split(".")[0]).split(os.path.sep)[0:-1])
        self.input_json_file: TextIO = open(
            os.path.join(test_dir, "test_resources", "job_generator_test_json.json"),
            "r",
        )
        self.parser = JsonParameterParser(self.input_json_file)
        self.jobGenerator: JobGenerator = JobGenerator(self.models, self.parser)
        self.jobGenerator_exception: JobGenerator = JobGenerator(
            self.models_exception, self.parser
        )

    def test_generate_right_amount_jobs(self) -> None:
        self.assertTrue(2 == len(self.jobGenerator.generate(self.subspace)))

    def test_first_job_has_right_subspace_dimensions(self) -> None:
        list_results: list[Result] = self.jobGenerator.generate(self.subspace)
        self.assertTrue(list_results[0].unpack().get_subspace_data().shape == (3, 3))
