from experiment.run.job import Job
from typing import Optional


class Result:
    """A Result instance is a result of a executed Job.
    """

    def __init__(self, job: Job = None, e: Exception = None) -> None:
        """constructor

        Args:
            job (job.Job): executed job
            e (Exception): Exception that was raised during execution of the job. Defaults to None.
        """
        self.job: Job = job
        self._e: Optional[Exception] = e

    def unpack(self) -> Job:
        """This method should be called by an Exporter.
        An Exception is raised if a Exception had been risen during the execution of the job that the Result contains.

        Raises:
            Exception that occured during the execution of the job.

        Returns:
            job.Job: Job that was successfully executed.
        """
        if self._e is None:
            return self.job
        else:
            raise self._e
