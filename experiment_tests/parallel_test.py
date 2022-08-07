import unittest
from pyod.models.knn import KNN
from pyod.models.ecod import ECOD
from pyod.models.abod import ABOD
from pyod.utils.data import generate_data
from experiment.run.job import Job
from experiment.run.parallel import Parallel, _MemoryManager
from experiment.supply.subspace.subspace import Subspace
from threading import Event
from queue import Queue
from multiprocessing.shared_memory import SharedMemory
import time
import numpy as np
import signal
import timeout_decorator


class ParallelRunnerTestCase(unittest.TestCase):

    timeout = 20

    def setUp(self) -> None:
        # handle ctrl-c so that this program can be shut down without resource leaking
        signal.signal(signal.SIGINT, self.signal_handler)
        # generate jobs
        self.job_list = list()
        self.subspace_list = list()
        for i in range(10):
            self.data_shape = (10, 3)
            data, y = generate_data(train_only=True, n_train=self.data_shape[0], n_features=self.data_shape[1])
            self.subspace_list.append(Subspace(data, None, np.ndarray([0, 1, 2])))

        for subspace in self.subspace_list:
            self.job_list.append(Job(subspace, KNN()))
            self.job_list.append(Job(subspace, ECOD()))
            self.job_list.append(Job(subspace, ABOD()))

        self.in_q = Queue()
        self.out_q = Queue()
        self.stop = Event()
        self.parallel = Parallel(self.in_q, self.out_q, self.stop, 4)

    def tearDown(self) -> None:
        self.stop.set()

    def signal_handler(self, signum, frame):
        print("revceived ctr+c: ", signum)
        self.stop.set()
        time.sleep(2)
        exit()

    @timeout_decorator.timeout(timeout)
    def test_parallel_terminate(self):
        self.parallel.start()
        time.sleep(1)
        self.stop.set()
        self.parallel.join(timeout=5)

    @timeout_decorator.timeout(timeout)
    def test_single_job(self):
        self.parallel.start()
        self.in_q.put(self.job_list[0])
        # self.in_q.put(self.job_list[1])
        self.assertEqual(self.out_q.get().unpack().get_outlier_scores().size, self.data_shape[0])

    @timeout_decorator.timeout(timeout)
    def test_multiple_jobs(self):
        self.parallel.start()
        for j in self.job_list:
            self.in_q.put(j)

        for i in range(len(self.job_list)):
            self.assertEqual(self.out_q.get().unpack().get_outlier_scores().size, self.data_shape[0])


class MemoryManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.data_shape = (10, 3)
        self.data_list: list[np.ndarray] = list()
        for i in range(10):
            data, y = generate_data(train_only=True, n_train=self.data_shape[0], n_features=self.data_shape[1])
            self.data_list.append(data)
        self.manager = _MemoryManager()

    def tearDown(self) -> None:
        self.manager.clean_up()

    def test_return_None_for_unregistered_share_name(self):
        self.assertTrue(self.manager.get_shared_memory_name(self.data_list[0]) is None)

    def test_register_subspace(self):
        data = self.data_list[0]
        self.manager.register_subspace(data)
        shm_name = self.manager.get_shared_memory_name(data)
        self.assertFalse(shm_name is None)
        shm = SharedMemory(shm_name)
        arr: np.ndarray = np.ndarray(shape=data.shape, dtype=data.dtype, buffer=shm.buf)
        # sanity check
        self.assertFalse(data is arr)
        self.assertTrue(np.array_equal(data, arr))
        self.manager.unregister_subspace(data)
        self.assertTrue(self.manager.get_shared_memory_name(data) is None)

    def test_multiple_register_single_subspace(self):
        iterations = 10
        data = self.data_list[0]
        for i in range(iterations):
            self.manager.register_subspace(data)
        shm_name = self.manager.get_shared_memory_name(data)
        self.assertFalse(shm_name is None)
        shm = SharedMemory(shm_name)
        arr: np.ndarray = np.ndarray(shape=data.shape, dtype=data.dtype, buffer=shm.buf)

        for i in range(iterations):
            self.assertFalse(data is arr)
            self.assertTrue(np.array_equal(data, arr))
            self.manager.unregister_subspace(data)

        self.assertTrue(self.manager.get_shared_memory_name(data) is None)

    def test_multiple_register_multiple_subspace(self):
        iterations = 10
        for data in self.data_list:
            for i in range(10):
                self.manager.register_subspace(data)

        for data in self.data_list:
            self.assertIsNotNone(self.manager.get_shared_memory_name(data))

        for data in self.data_list:
            shm_name = self.manager.get_shared_memory_name(data)
            shm = SharedMemory(shm_name)
            arr: np.ndarray = np.ndarray(shape=data.shape, dtype=data.dtype, buffer=shm.buf)
            self.assertTrue(np.array_equal(data, arr))

            for i in range(iterations):
                self.manager.unregister_subspace(data)

            self.assertIsNone(self.manager.get_shared_memory_name(data))
