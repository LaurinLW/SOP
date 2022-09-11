import abc


class ServerConnection(abc.ABC):
    """Abstract base class for all server connections
    """

    def __init__(self, server: str, experiment_id: str) -> None:
        """constructor

        Args:
            server (str): string that contains all necessary information
             needed to establish a connection to the server.
            experiment_id (str): unique identifier for the experiment
        """
        self._server = server
        self._experiment_id = experiment_id

    @abc.abstractmethod
    def send_progress(self, progress: int):
        """This method is used to update the server about the experiment's progress.

        Args:
            progress (int): progress of the experiment, as int in percent
        """
        pass

    @abc.abstractmethod
    def send_error(self, error: str):
        """This method is used to notify the server of errors that are not recoverable.

        Args:
            error (str): error message
        """
        pass

    @abc.abstractmethod
    def send_warning(self, warning: str):
        """This method is used to notify the server of recoverable errors that occured in execution.

        Args:
            warning (str): warning message
        """
        pass

    @abc.abstractmethod
    def send_result(self, name: str):
        """This method is used to notify the server of single results.

        Args:
            name (str): name of the result
        """
        pass
