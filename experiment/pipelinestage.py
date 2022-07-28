from threading import Event, Thread
from queue import Queue
from typing import TypeVar
import abc

T = TypeVar('T')
S = TypeVar('S')


class PipelineStage(Thread, abc.ABC):
    """This abstract class is the superclass of all PipelineStages. Each PipelineStage is a Thread.
    """
    @abc.abstractmethod
    def __init__(self, in_q: Queue[T], out_q: Queue[S], stop_stage: Event) -> None:
        """constructor

        Args:
            in_q (threading.Queue[T]): Queue for input
            out_q (threading.Queue[S]): Queue for output
            stop_stage (threading.Event): Event signaling that a stage should clean up and terminate
        """
        Thread.__init__(self)

        self._in_q: Queue[T] = in_q
        self._out_q: Queue[S] = out_q
        self._stop_stage: Event = stop_stage

        # timeout for queue access
        self._q_timeout: float = 1

    @abc.abstractmethod
    def run(self) -> None:
        """Entry-method of the Thread. Is run when start is called.
        """
        pass
