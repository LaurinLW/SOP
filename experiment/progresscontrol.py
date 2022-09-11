import experiment.export.exporter as ex
import experiment.connection.serverconnection as sc
import experiment.experimentmain as e
from typing import Optional


class ProgressControl:
    """This class keeps track of the experiments progress.
    An Export instance should update an instance of this class after each export.
    This class is also responsible for sending the progress to the server.
    After the last export the ProgressControl notifies the Experiment that it should stop via the stop()-method.
    """

    def __init__(self, experiment: e.Experiment, num_models: int, num_subspaces: int, server: sc.ServerConnection) -> None:
        """contructor

        Args:
            experiment (experiment.Experiment): running experiment
            num_models (int): number of models per subspace
            num_subspace (int):
            server (ServerConnection): ServerConnection object
            exporter (Exporter): exporter that notifies
        """
        self._experiment: e.Experiment = experiment
        self._subspace_runs: dict[tuple[str], int] = dict()
        self._num_models: int = num_models
        self._num_subspaces: int = num_subspaces
        self._server: sc.ServerConnection = server
        self._exporter: Optional[ex.Exporter]
        self._complete_subspaces = 0

    def update(self, subspace_dim: list[str]) -> None:
        """Exporters should call this method to update the progress of the Experiment.

        Args:
            subspace_dim (list[str]): dimension titles of the subspace
        """
        key: tuple[str] = tuple(subspace_dim)
        runs: dict[tuple[str], int]
        try:
            self._subspace_runs[key]
        except KeyError:
            self._subspace_runs[key] = 0

        self._subspace_runs[key] = self._subspace_runs[key] + 1

        if self._subspace_runs[key] == self._num_models:
            ex_file = self._exporter.finalize_single(subspace_dim)
            if ex_file is not None:
                self._server.send_result(ex_file)
            self._complete_subspaces += 1
            del self._subspace_runs[key]

        if self._complete_subspaces == self._num_subspaces:
            self._exporter.finalize()

        self._server.send_progress(self.get_progress())

        if self._complete_subspaces == self._num_subspaces:
            self._experiment.stop()

    def update_error(self, subspace_dim: list[str], error: Exception) -> None:
        """Exporters should call this method to notify Progresscontrol about errors

        Args:
            model (str): model which results would have been exported
            subspace_dim (list[str]): dimension titles of the subspace
            error (Exception): error that occured
        """
        self._server.send_warning(str(error))
        self.update(subspace_dim)

    def get_progress(self) -> int:
        """returns progress

        Returns:
            int: progress in percent as integer
        """
        sum_runs = self._complete_subspaces * self._num_models + sum(self._subspace_runs.values())
        total = self._num_models * self._num_subspaces
        return int((sum_runs / total) * 100)

    def register(self, exporter: ex.Exporter):
        """Registers an exporter that will be managed by the ProgressControl

        Args:
            exporter (ex.Exporter): Exporter that should be registered
        """
        self._exporter = exporter
