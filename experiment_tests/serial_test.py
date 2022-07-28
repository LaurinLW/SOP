import unittest
from pyod.models.knn import KNN
from pyod.models.ecod import ECOD
from pyod.utils.data import generate_data
from experiment.run.job import Job
from experiment.run.result import Result
from experiment.run.serial import Serial
from experiment.supply.subspace.subspace import Subspace
from threading import Event
from queue import Queue
import time


class SerialTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.data_shape = (10, 3)
        data, y = generate_data(train_only=True, n_train=self.data_shape[0], n_features=self.data_shape[1])
        dimension_names = ["1", "2", "3"]
        self.subspace = Subspace(data, dimension_names)
        self.jobs: list[Job] = [Job(self.subspace, KNN()), Job(self.subspace, ECOD())]

        self.in_q: Queue[Job] = Queue()
        self.out_q: Queue[Result] = Queue()
        self.stop = Event()
        self.serial = Serial(self.in_q, self.out_q, self.stop)

    def test_stop_no_jobs(self):
        self.serial.start()
        time.sleep(1)
        self.assertTrue(self.serial.is_alive())
        self.stop.set()
        # serial should terminate after at most a second
        self.serial.join(timeout=2)
        self.assertFalse(self.serial.is_alive())

    # test if jobs are properly completed
    def test_execute_job(self):
        self.serial.start()
        for j in self.jobs:
            self.in_q.put(j)
        for j in self.jobs:
            result = self.out_q.get()
            res_job = result.unpack()
            self.assertTrue(res_job.get_outlier_scores().size == self.data_shape[0])
        self.stop.set()

    # test what happens if out_q length is lower than the results that should be put into it
    def test_limited_out_q_length(self):
        lim_out_q: Queue[Result] = Queue(maxsize=1)
        lim_serial = Serial(self.in_q, lim_out_q, self.stop)
        lim_serial.start()

        for j in self.jobs:
            self.in_q.put(j)

        while self.in_q.qsize() >= len(self.jobs):
            time.sleep(0.001)

        for j in self.jobs:
            lim_out_q.get().unpack()

        self.stop.set()

    # test with model that throws an exception
    def test_throwing_model(self):
        throwing_job = Job(self.subspace, KNN(n_neighbors=self.data_shape[0] + 1))
        self.serial.start()
        self.in_q.put(throwing_job)
        for j in self.jobs:
            self.in_q.put(j)

        # first Result should throw
        self.assertRaises(Exception, self.out_q.get().unpack)

        # remaining jobs should be executed without problems
        for j in self.jobs:
            self.out_q.get().unpack()
        self.stop.set()
