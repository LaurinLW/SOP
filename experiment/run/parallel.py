from experiment.run.runner import Runner
from experiment.run.job import Job
from experiment.run.result import Result
from queue import Queue
from threading import Event
from multiprocessing.shared_memory import SharedMemory
from typing import Optional
import pyod
import numpy as np
import multiprocessing as mp


class Parallel(Runner):
    """This class is a Runner implementation that runs multiple Jobs in parallel."""

    def __init__(
        self, in_q: Queue[Job], out_q: Queue[Result], stop_stage: Event, num_procs: int
    ):
        super().__init__(in_q, out_q, stop_stage)
        self._num_procs: int = num_procs
        self._id_counter: int = 0
        self._manager: _MemoryManager = _MemoryManager()
        # local queues for processes
        self._queue_manager: mp.managers.SyncManager = mp.Manager()
        self._l_q_in: Queue[_Local_Job] = self._queue_manager.Queue()
        self._l_q_out: Queue[_Local_Job] = self._queue_manager.Queue()
        # to avoid loading to much data in shared memory
        self._execution_limit = 2 * num_procs
        # map jobs to id for proper
        self._job_dict: dict[int, Job] = dict()
        self._next_job: Optional[Job] = None
        self._next_local_job: Optional[_Local_Job] = None
        self._next_result: Optional[Result] = None

    def run(self):
        # beware: Processes should only be terminated when the queues are no longer needed. Otherwise the queues(local) may be corrupted
        processes = [
            mp.Process(target=_process_execution, args=(self._l_q_in, self._l_q_out))
            for i in range(self._num_procs)
        ]
        for p in processes:
            p.start()

        while not self._stop_stage.is_set():
            self._get_jobs()
            self._export_finished()

        for p in processes:
            p.terminate()
        self._manager.clean_up()

    def _get_jobs(self):
        """Gets jobs from in_q, loads shared memory, puts jobs in the local execution queue"""
        while (
            len(self._job_dict) <= self._execution_limit or (self._next_job is not None)
        ) and not self._stop_stage.is_set():
            if self._next_job is None:

                try:
                    self._next_job = self._in_q.get(timeout=self._q_timeout)
                except Exception:
                    # could not get job
                    # sanity check
                    assert self._next_job is None
                    break

                self._manager.register_subspace(self._next_job.get_subspace_data())

                j_id = self._id_counter
                self._id_counter += 1
                self._job_dict[j_id] = self._next_job
                data: np.ndarray = self._next_job.get_subspace_data()
                self._next_local_job = _Local_Job(
                    self._next_job.model,
                    self._manager.get_shared_memory_name(
                        self._next_job.get_subspace_data()
                    ),
                    j_id,
                    data.dtype,
                    data.shape,
                )

            try:
                self._l_q_in.put(item=self._next_local_job, timeout=self._q_timeout)
                self._next_job = None
            except Exception:
                # currently cannot enter another job
                break

    def _export_finished(self):
        # escapes loop as soon as an exeption is thrown
        while not self._stop_stage.is_set():
            if self._next_result is None:
                try:
                    self._next_local_job = self._l_q_out.get(timeout=self._q_timeout)
                    if self._next_local_job.e is None:
                        job = self._job_dict[self._next_local_job.j_id]
                        job.model = self._next_local_job.model
                        self._next_result = Result(job)
                    else:
                        self._next_result = Result(
                            self._job_dict[self._next_local_job.j_id],
                            self._next_local_job.e,
                        )
                except Exception:
                    # No finished Job available
                    break

            try:
                self._out_q.put(item=self._next_result, timeout=self._q_timeout)
                self._next_result = None
                data = self._job_dict[self._next_local_job.j_id].get_subspace_data()
                self._manager.unregister_subspace(data)
                del self._job_dict[self._next_local_job]
            except Exception:
                # cannot export Result
                break


class _Local_Job:
    """simple record class holding job information for processes"""

    def __init__(
        self,
        model: pyod.models.base.BaseDetector,
        shm_name: str,
        j_id: int,
        dtype: np.dtype,
        data_shape: np.shape,
    ):
        self.model: pyod.models.BaseDetector = model
        self.shm_name: str = shm_name
        self.j_id: int = j_id
        self.dtype: np.dtype = dtype
        self.data_shape: np.shape = data_shape
        self.e: Optional[Exception] = None


def _process_execution(l_q_in: Queue[_Local_Job], l_q_out: Queue[_Local_Job]):
    # optimization idea: check if the given shm was already loaded in previous job and reuse it
    while True:
        shm: Optional[SharedMemory] = None
        loc_job = l_q_in.get()
        # Extra catch for shm. If shm was created it should be closed at the end.
        try:
            shm = SharedMemory(loc_job.shm_name)
        except Exception as e:
            loc_job.e = e

        if shm is not None:
            try:
                data: np.ndarray = np.ndarray(
                    shape=loc_job.data_shape, dtype=loc_job.dtype, buffer=shm.buf
                )
                loc_job.model.fit(data)

            except Exception as e:
                loc_job.e = e

            shm.close()

        l_q_out.put(loc_job)


class _MemoryManager:
    def __init__(self) -> None:
        self._registered_count: list[tuple[np.ndarray, int]] = list()
        self._memory_mapping: list[tuple[np.ndarray, SharedMemory]] = list()

    def register_subspace(self, data: np.ndarray) -> None:
        """Should be called before each job execution.
        Creates shared memory for the subspace data in case that the data is not already loaded into shared memory.

        Args:
            data (np.ndarray): subspace data that gets registered
        """
        count = self._get_registered_count(data)
        if count == 0:
            self._registered_count.append((data, 1))
            self._memory_mapping.append((data, self._create_shared_memory(data)))
        else:
            # increment count
            self._registered_count_add(data, 1)

    def unregister_subspace(self, data: np.ndarray) -> None:
        """When a Job is done, this method should be called with its subspace data.
        Destroys shared memory if it is no longer needed.

        Args:
            data (np.ndarray): subspace data that should be unregistered
        """
        count = self._get_registered_count(data)
        if count == 0:
            return

        if count <= 1:
            # request that underlying shared memory should be destroyed
            self._get_shared_memory(data).close()
            self._get_shared_memory(data).unlink()
            _MemoryManager._delete_tuple_from_list(data, self._memory_mapping)
            _MemoryManager._delete_tuple_from_list(data, self._registered_count)
        else:
            self._registered_count_add(data, -1)

    def get_shared_memory_name(self, data: np.ndarray) -> Optional[str]:
        """
        Args:
            data (np.ndarray): subspace data whose shared memory name is requested

        Returns:
            Optional[str]: shared memory name, if the subspace data is not registered None
        """
        shm: SharedMemory = self._get_shared_memory(data)
        if shm is None:
            return None
        else:
            return shm.name

    def _get_shared_memory(self, data: np.ndarray) -> SharedMemory:
        list: list[tuple[np.ndarray, SharedMemory]] = [
            item for item in self._memory_mapping if item[0] is data
        ]
        if len(list) == 0:
            return None
        else:
            return list[0][1]

    def _create_shared_memory(self, data: np.ndarray) -> SharedMemory:
        """Creates a shared memory segment for the given subspace data and copies the the Subspace data into shared memory

        Args:
            data (np.ndarray): data that is copied into a shared memory segment

        Returns:
            SharedMemory: shared memory segment containing the data of subspace
        """
        size: int = data.nbytes
        shm = SharedMemory(create=True, size=size)
        # load data contents into shared memory
        arr = np.ndarray(shape=data.shape, dtype=data.dtype, buffer=shm.buf)
        np.copyto(dst=arr, src=data)

        return shm

    def _get_registered_count(self, data: np.ndarray) -> int:
        list = [item for item in self._registered_count if item[0] is data]
        if len(list) == 0:
            return 0
        else:
            return (list[0])[1]

    def _registered_count_add(self, data: np.ndarray, add: int) -> None:
        for i in range(len(self._registered_count)):
            if self._registered_count[i][0] is data:
                element = self._registered_count.pop(i)
                self._registered_count.append((element[0], element[1] + add))
                return

    def _delete_tuple_from_list(first_tuple_value, list) -> None:
        for i in range(len(list)):
            if list[i][0] is first_tuple_value:
                list.pop(i)
                return

    def clean_up(self):
        """Unlinks all shared memory segments. Cleans up all segments.
        Should be called on exit to avoid leaking resources
        """
        for d, shm in self._memory_mapping:
            shm.close()
            shm.unlink()

        # reset lists in case that the object will be used again
        self._memory_mapping = list()
        self._registered_count = list()
