from experiment.connection.serverconnection import ServerConnection
import requests


class RPCServerConnection(ServerConnection):
    """A server connection utilizing rpc
    """

    def __init__(self, server: str, experiment_id: str):
        super().__init__(server, experiment_id)
        self._json_id = 0

    def send_progress(self, progress: int):
        payload = self._create_payload("receiveProgress", [progress, self._experiment_id])
        requests.post(self._server, json=payload)

    def send_error(self, error: str):
        payload = self._create_payload("receiveError", [error, self._experiment_id])
        requests.post(self._server, json=payload)

    def send_warning(self, warning: str):
        payload = self._create_payload("receiveWarning", [warning, self._experiment_id])
        requests.post(self._server, json=payload)

    def send_result(self, name: str):
        payload = self._create_payload("receiveResult", [name, self._experiment_id])
        requests.post(self._server, json=payload)

    def _create_payload(self, method: str, parameters: list) -> dict:
        paylaod = {
            "method": method,
            "params": parameters,
            "jsonrpc": "2.0",
            "id": self._json_id,
        }

        self._json_id += 1

        return paylaod
