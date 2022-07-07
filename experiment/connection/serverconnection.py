import abc


class ServerConnection(abc.ABC):
    def __init__(self, server: str, experiment_id: str) -> None:
        self._server = server
        self._experiment_id = experiment_id

    def send_progress(self, progress: int):
        pass

    def send_error(self, error: str):
        pass
