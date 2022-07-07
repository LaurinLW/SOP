import abc
import progresscontrol
import pipelinestage
import threading
import run.result as result


class Exporter(pipelinestage.PipelineStage, abc.ABC):
    """This abstract class is the super class of all export pipeline stages.
    """
    @abc.abstractmethod
    def __init__(self, progress: progresscontrol.ProgressControl, in_q: threading.Queue[result.Result], stop: threading.Event) -> None:
        super.__init__(in_q=in_q, out_q=None, stop=stop)
        self._progress = progress

    @abc.abstractmethod
    def finalize() -> None:
        """Should be called by ProgressControl after last export. Creates a valid final state of all exports.
        """
        pass
