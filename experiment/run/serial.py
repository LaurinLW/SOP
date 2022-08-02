from queue import Empty
from experiment.run.runner import Runner
from experiment.run.result import Result
from experiment.run.job import Job
from threading import Event
from queue import Queue
from typing import Optional


class Serial(Runner):
    """A Runner implementation that runs one Job at a time."""

    def __init__(self, in_q: Queue[Job], out_q: Queue[Result], stop_stage: Event):
        """constructor

        Args:
            in_q (Queue[Job]): _description_
            out_q (Queue[Result]): _description_
            stop_stage (Event): _description_
        """
        super().__init__(in_q, out_q, stop_stage)

    def run(self):
        """method called when stage is started. Entrypoint for this pipeline stage
        """
        result: Optional[Result] = None

        while not self._stop_stage.is_set():
            # put result
            if result is not None:
                try:
                    self._out_q.put(result, timeout=self._q_timeout)
                    result = None
                except Exception:
                    # if you cannot place result in queue, check event flag and try again
                    continue

            # get and execute new job
            try:
                current_job = self._in_q.get(timeout=self._q_timeout)
                result = self.__execute(current_job)
            except Empty:
                # In the case that no item is available after timeout an exception is thrown.
                # Does not need any explicit handling
                pass

    def __execute(self, job: Job) -> Result:
        try:
            job.model.fit(job.get_subspace_data())
            return Result(job)
        except Exception as e:
            return Result(job=job, e=e)
