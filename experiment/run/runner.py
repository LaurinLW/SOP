from experiment.run.job import Job
from experiment.run.result import Result
from experiment.pipelinestage import PipelineStage
from threading import Event
from queue import Queue
import abc


class Runner(PipelineStage, abc.ABC):
    """Abstract superclass for all runner pipeline stages.
    """

    def __init__(self, in_q: Queue[Job], out_q: Queue[Result], stop_stage: Event):
        """constructor

        Args:
            in_q (Queue[Job]): Queue that supplies the Runner with Jobs
            out_q (Queue[Result]): Queue that receives Results from the Runner
            stop_stage (Event): Event signaling that the Runner should clean up and terminate
        """
        super().__init__(in_q=in_q, out_q=out_q, stop_stage=stop_stage)
