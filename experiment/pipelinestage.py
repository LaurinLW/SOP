import threading
import abc
from typing import TypeVar

T = TypeVar('T')
S = TypeVar('S')


class PipelineStage(threading.Thread, abc.ABC):
    """This abstract class is the superclass of all PipelineStages. Each PipelineStage is a Thread.
    """
    @abc.abstractmethod
    def __init__(self, in_q: threading.Queue[T], out_q: threading.Queue[S], stop: threading.Event) -> None:
        """constructor

        Args:
            in_q (threading.Queue[T]): Queue for input
            out_q (threading.Queue[S]): Queue for output
            stop (threading.Event): Event signaling that a stage should clean up and terminate
        """
        self._in_q = in_q
        self._out_q = out_q
        self._stop = stop

    @abc.abstractmethod
    def run(self) -> None:
        """Entry-method of the Thread. Is run when start is called.
        """
        pass
