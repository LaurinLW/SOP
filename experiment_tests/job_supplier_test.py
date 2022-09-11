import unittest
import numpy as np
from typing import TextIO
import os

from django.forms import JSONField
from multiprocessing import Queue
from pandas import DataFrame
from threading import Event
from experiment.run.job import Job

from experiment.supply.job_supplier import JobSupplier
from experiment.supply.parser.parameter_parser_json import JsonParameterParser


class JobSupplierTest(unittest.TestCase):
    def setUp(self):
        self.number_subspaces: int = 2
        self.min_dimension: int = 1
        self.max_dimension: int = 3
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
        test_dir = (os.path.sep).join((__file__.split(".")[0]).split(os.path.sep)[0:-1])
        self.file: TextIO = open(
            os.path.join(test_dir, "test_resources", "job_generator_test_json.json"),
            "r",
        )
        self.parser: JsonParameterParser = JsonParameterParser(self.file)
        self.out: Queue = Queue(4)
        self.stop: Event = Event()
        self.jobSupplier: JobSupplier = JobSupplier(
            self.number_subspaces,
            self.min_dimension,
            self.max_dimension,
            self.seed,
            self.data,
            self.models,
            self.parser,
            self.out,
            self.stop,
        )

        self.jobSupplier_exception: JobSupplier = JobSupplier(
            self.number_subspaces,
            self.min_dimension,
            self.max_dimension,
            self.seed,
            self.data,
            self.models,
            self.file,
            self.out,
            self.stop,
        )

    def test_amount_elements_queue(self) -> None:
        self.jobSupplier.run()
        self.assertTrue(self.out.full())

    def test_amount_elements_queue_empty(self) -> None:
        self.jobSupplier.run()
        self.out.get()
        self.out.get()
        self.out.get()
        self.out.get()
        self.assertTrue(self.out.empty())

    def test_is_job(self) -> None:
        self.jobSupplier.run()
        self.assertTrue(
            isinstance(self.out.get().unpack(), Job) and self.out.get()._e is None
        )

    def test_is_exception(self) -> None:
        self.jobSupplier_exception.run()
        self.assertTrue(self.out.get()._e is not None)
