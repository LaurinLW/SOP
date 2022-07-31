import experiment.export.exporter as ex
import experiment.connection.serverconnection as sc
from experiment.experiment import Experiment


class ProgressControl:
    """This class keeps track of the experiments progress.
    An Export instance should update an instance of this class after each export.
    This class is also responsible for sending the progress to the server.
    After the last export the ProgressControl notifies the Experiment that it should stop via the stop()-method.
    """

    def __init__(self, experiment: Experiment, num_model_runs: dict[str, int], server: sc.ServerConnection) -> None:
        """contructor

        Args:
            experiment (experiment.Experiment): running experiment
            num_model_runs (dict[str, int]): dictionary with model names as key and number of runs as value
            server (ServerConnection): ServerConnection object
            exporter (Exporter): exporter that notifies
        """
        pass

    def update(self, model: str, subspace_dim: list[str]) -> None:
        """Exporters should call this method to update the progress of the Experiment.

        Args:
            model (str): model which results were exported
            subspace_dim (list[str]): dimension titles of the subspace
        """
        pass

    def update_error(self, model: str, subspace_dim: list[str], error: Exception) -> None:
        """Exporters should call this method to notify Progresscontrol about errors

        Args:
            model (str): model which results would have been exported
            subspace_dim (list[str]): dimension titles of the subspace
            error (Exception): error that occured
        """
        pass

    def get_progress() -> int:
        """returns progress

        Returns:
            int: progress in percent as integer
        """
        pass

    def register(self, exporter: ex.Exporter):
        """Registers an exporter that will be managed by the ProgressControl

        Args:
            exporter (ex.Exporter): Exporter that should be registered
        """
        pass
