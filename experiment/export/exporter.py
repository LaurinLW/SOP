import abc
import threading
from experiment.pipelinestage import PipelineStage
from experiment.run.result import Result
from queue import Queue

# avoids circular import caused by typchecking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from experiment.progresscontrol import ProgressControl


class Exporter(PipelineStage, abc.ABC):
    """This abstract class is the super class of all export pipeline stages.
    """
    @abc.abstractmethod
    def __init__(self, progress: "ProgressControl", in_q: Queue[Result], stop_stage: threading.Event) -> None:
        super().__init__(in_q=in_q, out_q=None, stop_stage=stop_stage)
        self._progress = progress

    @abc.abstractmethod
    def finalize(self) -> None:
        """Should be called by ProgressControl after last export. Creates a valid final state of all exports.
        """
        pass

    @abc.abstractmethod
    def finalize_single(self, dims: list[str]) -> str:
        """Exports single subspace.

        Args:
            dims (list[str]): list of dimensions of the export

        Returns:
            name of export
        """
        pass
