from queue import Empty
from experiment.run.runner import Runner
from experiment.run.result import Result
from experiment.run.job import Job
from threading import Event
from queue import Queue
from typing import Optional
from pyod.models.base import BaseDetector


class Serial(Runner):
    """A Runner implementation that runs one Job at a time."""

    def __init__(self, in_q: Queue[Result], out_q: Queue[Result], stop_stage: Event):
        """constructor

        Args:
            in_q (Queue[Result]): Queue with incoming jobs(as Result objects)
            out_q (Queue[Result]): Queue receiving finished jobs(as Result objects)
            stop_stage (Event): Event Responsible for stopping the pipelinstage
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

    def __execute(self, input_result: Result) -> Result:
        job: Job

        try:
            job = input_result.unpack()
        except Exception:
            # if the input is already broken just pass it along
            return input_result

        try:
            model: BaseDetector = job.get_model_class()(**job.get_parameters())
            model.fit(job.get_subspace_data())
            job.set_model_result(str(model), model.decision_scores_)
            return Result(job)
        except Exception as e:
            return Result(job=job, e=e)
