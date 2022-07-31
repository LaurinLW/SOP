import unittest
import threading
from experiment.export.csvexporter import CSVExporter
from experiment.run.result import Result
from experiment.run.job import Job
from queue import Queue
from experiment.progresscontrol import ProgressControl
import os
from pyod.utils import generate_data
from pyod.models.abod import ABOD
from pyod.models.kde import KDE
from pyod.models.sod import SOD
from experiment.supply.subspace.subspace import Subspace
from experiment.run.result import Result
import time
import pandas as pd
import numpy as np
from experiment.export.exporter import Exporter

# TODO missing tests involving proper ProgressControll


class CSVExporterTest(unittest.TestCase):

    export_dir = "export"
    export_path = ""

    @classmethod
    def setUpClass(cls):
        test_dir = (os.path.sep).join((__file__.split(".")[0]).split(os.path.sep)[0:-1])
        print(test_dir)
        cls.export_path = os.path.join(test_dir, cls.export_dir)
        if not os.path.exists(cls.export_path):
            os.mkdir(cls.export_path)
        else:
            for f in os.listdir(cls.export_path):
                # there should not be any subdirectories in the directory
                os.remove(os.path.join(cls.export_path, f))

    def setUp(self):
        self.in_q = Queue()
        self.stop_stage = threading.Event()
        self.export_path = CSVExporterTest.export_path
        self.exporter = CSVExporter(MockProgressControl(), self.in_q, self.stop_stage, self.export_path)
        self.data = list()
        self.models = [SOD, ABOD, KDE]
        self.num_subspaces = 3
        for i in range(self.num_subspaces):
            X, y = generate_data(train_only=True, n_train=100, n_features=3)
            self.data.append(X)
        self.fitted_models = list()
        for d in self.data:
            for m in self.models:
                model = m()
                model.fit(d)
                self.fitted_models.append(model)
        self.results = list()
        for i, d in enumerate(self.data):
            dimensions = list()
            for j in range(d.shape[1]):
                dimensions.append(f"dim{j},{i}")
            for j in range(len(self.models)):
                subspace = Subspace(d, dimensions)
                job = Job(subspace, self.fitted_models[len(self.models)*i+j])
                self.results.append(Result(job))

        delete_directory_contents(self.export_path)
        self.exporter.start()

    def tearDown(self):
        self.stop_stage.set()

    def test_single_result(self):
        self.in_q.put(self.results[0])
        # to make sure data is handled, in real used finalize is only called after all results are handled
        time.sleep(1)
        self.exporter.finalize()
        df = pd.read_csv(os.path.join(CSVExporterTest.export_path, "subspace_result0.csv"), dtype=np.float64)
        df_arr = df.to_numpy(dtype=np.float64)
        # even though the values are only read pandas introduces small changes to values
        self.assertTrue(np.allclose(df_arr[:, 1:-1], self.data[0]))
        self.assertTrue(np.allclose(df_arr[:, -1], self.fitted_models[0].decision_scores_))

    def test_multiple_results(self):
        for r in self.results:
            self.in_q.put(r)

        time.sleep(2)
        self.exporter.finalize()

        for i, data in enumerate(self.data):
            df: pd.DataFrame = pd.read_csv(os.path.join(CSVExporterTest.export_path, f"subspace_result{i}.csv"), dtype=np.float64)
            df_arr = df.to_numpy(dtype=np.float64)
            columns: int = data.shape[1]
            # check input data
            # first column contains indices
            self.assertTrue(np.allclose(df_arr[:, 1:columns+1], data))
            # check scores
            for j in range(len(self.models)):
                df_scores = df[str(self.fitted_models[i*len(self.models)+j])]
                m_scores = self.fitted_models[i*len(self.models)+j].decision_scores_
                self.assertTrue(np.allclose(df_scores, m_scores))

    def test_no_result(self):
        self.exporter.finalize()
        self.stop_stage.set()
        self.exporter.join()

    def test_finalize_single(self):
        for r in self.results:
            self.in_q.put(r)

        time.sleep(2)

        self.exporter.finalize_single(self.results[0].unpack().get_subspace_dimensions())

        data = self.data[0]
        df: pd.DataFrame = pd.read_csv(os.path.join(CSVExporterTest.export_path, "subspace_result0.csv"), dtype=np.float64)
        df_arr = df.to_numpy(dtype=np.float64)
        columns: int = data.shape[1]
        # check input data
        # first column contains indices
        self.assertTrue(np.allclose(df_arr[:, 1:columns+1], data))
        # check scores
        for j in range(len(self.models)):
            df_scores = df[str(self.fitted_models[j])]
            m_scores = self.fitted_models[j].decision_scores_
            self.assertTrue(np.allclose(df_scores, m_scores))


def delete_directory_contents(path):
    for f in os.listdir(path):
        # there should not be any subdirectories in the directory
        os.remove(os.path.join(path, f))


class MockProgressControl:
    # A ProgressControl for testing. Does not require Server
    def __init__(self):
        pass

    def update(self, model: str, subspace_dim: list[str]) -> None:
        pass

    def update_error(self, model: str, subspace_dim: list[str], error: Exception) -> None:
        pass

    def register(self, exporter: Exporter):
        pass
