import job


class Resulst:
    def __init__(self, job: job.Job, e: Exception) -> None:
        self._job = job
        self._e = e

    def unpack() -> job.Job:
        pass
