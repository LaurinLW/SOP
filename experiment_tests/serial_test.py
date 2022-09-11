import unittest
import numpy as np
from pyod.models.knn import KNN
from pyod.models.ecod import ECOD
from pyod.models.abod import ABOD
from pyod.utils.data import generate_data
from experiment.run.job import Job
from experiment.run.result import Result
from experiment.run.serial import Serial
from experiment.supply.subspace.subspace import Subspace
from threading import Event
from queue import Queue
import time
import timeout_decorator


class SerialTestCase(unittest.TestCase):

    timeout = 20

    def setUp(self) -> None:
        self.data_shape = (10, 3)
        data, y = generate_data(train_only=True, n_train=self.data_shape[0], n_features=self.data_shape[1])
        dimension_names = ["1", "2", "3"]
        self.subspace = Subspace(data, dimension_names, np.ndarray([0, 1, 2]))
        self.jobs: list[Job] = [Job(self.subspace, KNN, dict()), Job(self.subspace, ECOD, dict()), Job(self.subspace, ABOD, dict())]
        self.input_results: list[Result] = [Result(j) for j in self.jobs]

        self.in_q: Queue[Result] = Queue()
        self.out_q: Queue[Result] = Queue()
        self.stop = Event()
        self.serial = Serial(self.in_q, self.out_q, self.stop)

    @timeout_decorator.timeout(timeout)
    def test_stop_no_jobs(self):
        self.serial.start()
        time.sleep(1)
        self.assertTrue(self.serial.is_alive())
        self.stop.set()
        # serial should terminate after at most a second
        self.serial.join(timeout=2)
        self.assertFalse(self.serial.is_alive())

    # test if jobs are properly completed
    @timeout_decorator.timeout(timeout)
    def test_execute_job(self):
        self.serial.start()
        for j in self.input_results:
            self.in_q.put(j)
        for j in self.input_results:
            result = self.out_q.get()
            res_job = result.unpack()
            self.assertTrue(res_job.get_outlier_scores().size == self.data_shape[0])
        self.stop.set()

    # test what happens if out_q length is lower than the results that should be put into it
    @timeout_decorator.timeout(timeout)
    def test_limited_out_q_length(self):
        lim_out_q: Queue[Result] = Queue(maxsize=1)
        lim_serial = Serial(self.in_q, lim_out_q, self.stop)
        lim_serial.start()

        for j in self.input_results:
            self.in_q.put(j)

        while self.in_q.qsize() >= len(self.input_results) - 1:
            time.sleep(0.01)

        # work around. Wait for second job finish. Goal: serial is unable to put in out_q
        # no sleep would be better, but there is no way to look into the internals of the object
        time.sleep(4)

        for j in self.input_results:
            lim_out_q.get().unpack()

        self.stop.set()

    # test with model that throws an exception
    @timeout_decorator.timeout(timeout)
    def test_throwing_model(self):
        throwing_job_result = Result(Job(self.subspace, KNN, {"n_neihbors": self.data_shape[0] + 1}))
        self.serial.start()
        self.in_q.put(throwing_job_result)
        for j in self.input_results:
            self.in_q.put(j)

        # first Result should throw
        self.assertRaises(Exception, self.out_q.get().unpack)

        # remaining jobs should be executed without problems
        for j in self.input_results:
            self.out_q.get().unpack()
        self.stop.set()

    @timeout_decorator.timeout(timeout)
    def test_result_with_exception(self):
        exception_result = Result(Job(), Exception("Test"))

        self.serial.start()
        self.in_q.put(exception_result)
        for j in self.input_results:
            self.in_q.put(j)

        # first Result should throw
        self.assertRaises(Exception, self.out_q.get().unpack)

        # remaining jobs should be executed without problems
        for j in self.input_results:
            self.out_q.get().unpack()
        self.stop.set()
