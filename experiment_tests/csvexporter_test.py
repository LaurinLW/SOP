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
import time
import pandas as pd
import numpy as np
from experiment.export.exporter import Exporter
import timeout_decorator

# TODO missing tests involving proper ProgressControll


class CSVExporterTest(unittest.TestCase):

    timeout = 30

    export_dir = "export"
    export_path = ""

    @classmethod
    def setUpClass(cls):
        test_dir = (os.path.sep).join((__file__.split(".")[0]).split(os.path.sep)[0:-1])
        cls.export_path = os.path.join(test_dir, cls.export_dir)
        if not os.path.exists(cls.export_path):
            os.mkdir(cls.export_path)
        else:
            for f in os.listdir(cls.export_path):
                # there should not be any subdirectories in the directory
                os.remove(os.path.join(cls.export_path, f))

    def setUp(self):
        self.verifier = _ExportVerifier()
        self.in_q = Queue()
        self.stop_stage = threading.Event()
        self.export_path = CSVExporterTest.export_path
        self.progresscontrol = MockProgressControl()
        self.exporter = CSVExporter(self.progresscontrol, self.in_q, self.stop_stage, self.export_path)
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
            indices = np.array([i for i in range(d.shape[0])], np.uint32)
            for j in range(d.shape[1]):
                dimensions.append(f"dim{j},{i}")
            for j in range(len(self.models)):
                subspace = Subspace(d, dimensions, indices)
                job = Job(subspace, self.models[j], dict())
                fit_model = self.fitted_models[len(self.models) * i + j]
                job.set_model_result(str(fit_model), fit_model.decision_scores_)
                self.results.append(Result(job))

        delete_directory_contents(self.export_path)
        self.exporter.start()

    def tearDown(self):
        self.stop_stage.set()

    @timeout_decorator.timeout(timeout)
    def test_single_result(self):
        self.in_q.put(self.results[0])
        # to make sure data is handled, in real used finalize is only called after all results are handled
        # time.sleep(1)
        self.progresscontrol.wait(1)

        self.exporter.finalize()

        self.verifier.load(self.export_path)

        self.assertTrue(self.verifier.verify_job(self.results[0].unpack()))

    @timeout_decorator.timeout(timeout)
    def test_multiple_results(self):
        for r in self.results:
            self.in_q.put(r)

        self.progresscontrol.wait(len(self.results))

        self.exporter.finalize()

        self.verifier.load(self.export_path)

        for r in self.results:
            if not self.verifier.verify_job(r.unpack()):
                self.fail("verification failed")

    @timeout_decorator.timeout(timeout)
    def test_no_result(self):
        self.exporter.finalize()
        self.stop_stage.set()
        self.exporter.join()

    @timeout_decorator.timeout(timeout)
    def test_finalize_single(self):
        for r in self.results:
            self.in_q.put(r)

        self.progresscontrol.wait(len(self.results))

        self.exporter.finalize_single(self.results[0].unpack().get_subspace_dimensions())

        self.verifier.load(self.export_path)

        self.assertTrue(self.verifier.verify_job(self.results[0].unpack()))

    @timeout_decorator.timeout(timeout)
    def test_export_failed_job(self):
        base_job = self.results[0].unpack()
        failed_job_model = Result(base_job, e=Exception("arbitrary runtime exception"))
        failed_job_no_model = Result(Job(Subspace(base_job.get_subspace_data(),
                                                  base_job.get_subspace_dimensions(),
                                                  base_job.get_indexes_after_clean()), None))

        self.in_q.put(failed_job_model)
        self.in_q.put(failed_job_no_model)

        for r in self.results:
            self.in_q.put(r)

        self.progresscontrol.wait(len(self.results) + 2)

        self.exporter.finalize()

        self.verifier.load(self.export_path)
        for r in self.results:
            if not self.verifier.verify_job(r.unpack()):
                self.fail("failed verification")

    @timeout_decorator.timeout(timeout)
    def test_finalize_single_non_existing(self):
        for r in self.results:
            self.in_q.put(r)

        self.progresscontrol.wait(len(self.results))

        self.exporter.finalize_single(["does", "not", "exist", "46290"])
        self.exporter.finalize()
        self.verifier.load(self.export_path)

        for r in self.results:
            if not self.verifier.verify_job(r.unpack()):
                self.fail("failed verification")

    @timeout_decorator.timeout(timeout)
    def test_error_messages(self):
        subspace = Subspace(self.data[0], ["dim1", "dim2", "dim3"], [i for i in range(self.data[0].shape[0])])
        error_no_class = Result(Job(subspace, None, None), Exception("Test Exception"))
        error_class_params = Result(Job(subspace, KDE, {"contamination": 0.1}), Exception("Another Test Exception"))
        succeeding_job = Job(subspace, KDE, dict())
        model = KDE()
        model.fit(succeeding_job.get_subspace_data())
        succeeding_job.set_model_result(str(model), model.decision_scores_)
        succeeding_result = Result(succeeding_job)

        self.in_q.put(error_no_class)
        self.in_q.put(error_class_params)
        self.in_q.put(succeeding_result)

        self.progresscontrol.wait(2)
        self.exporter.finalize()

        df = pd.read_csv(os.path.join(self.export_path, "subspace_result0.csv"))

        self.verifier.load(self.export_path)
        self.assertTrue(self.verifier.verify_job(succeeding_job))
        # index + 3 subspace dim + 2 results
        self.assertEqual(len(df.columns), 7)


def delete_directory_contents(path):
    for f in os.listdir(path):
        # there should not be any subdirectories in the directory
        os.remove(os.path.join(path, f))


class _ExportVerifier:

    def load(self, path: str):
        """Loads all export files into memory

        Args:
            path (str): path to export directory
        """
        self._dataframes: list[pd.DataFrame] = list()

        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            self._dataframes.append(pd.read_csv(file_path))

    def verify_job(self, job: Job) -> bool:
        """Verifies that the outlierscores of the given job are in the export files(in the file with the corressponding subspace).
        Only works for jobs having a model.

        Args:
            job (Job): job that gets verified

        Returns:
            bool: true if the jobs outlierscores are in the exports, false else
        """
        df: pd.DataFrame = self._find_dataframe(job.get_subspace_data())
        if df is None:
            return False

        return np.allclose(df[job.get_model_string()].to_numpy(), job.get_outlier_scores(), equal_nan=True)

    def _find_dataframe(self, subspace: np.ndarray) -> pd.DataFrame:
        """Finds fitting dataframe for given subspace data

        Args:
            subspace (np.ndarray): subspace data

        Returns:
            pd.DataFrame: A fitting Dataframe, None if there is no fitting Dataframe
        """
        columns = subspace.shape[1]

        for df in self._dataframes:
            if len(df.columns) < columns:
                continue

            # first column is indices
            df_sp = df.iloc[:, 1:columns + 1].to_numpy(dtype=subspace.dtype)
            if np.allclose(subspace, df_sp, equal_nan=True):
                return df

        return None


class MockProgressControl(ProgressControl):
    # A ProgressControl for testing. Does not require Server
    def __init__(self):
        self.count = 0

    def update(self, subspace_dim: list[str]) -> None:
        self.count += 1

    def update_error(self, subspace_dim: list[str], error: Exception) -> None:
        self.count += 1

    def register(self, exporter: Exporter):
        pass

    def wait(self, num_jobs: int):
        """Help function. Returns as soon as the MockProgressControl is notified num_jobs jobs

        Args:
            num_jobs (int): number of jobs waiting for notifying
        """
        while(self.count < num_jobs):
            time.sleep(0.1)
