from experiment.connection.serverconnection import ServerConnection
import requests


class RPCServerConnection(ServerConnection):
    """A server connection utilizing rpc
    """

    def __init__(self, server: str, experiment_id: str):
        super.__init__(self, server, experiment_id)
        self._json_id = 0

    def send_progress(self, progress: int):
        payload = self._create_payload("receiveProgress", [progress, self._experiment_id])
        requests.post(self._server, json=payload).json()

    def send_error(self, error: str):
        payload = self._create_payload("receiveError", [error, self._experiment_id])
        requests.post(self._server, json=payload).json()

    def _create_payload(self, method: str, parameters: list) -> dict:
        paylaod = {
            "method": method,
            "params": parameters,
            "jsonrpc": "2.0",
            "id": self._json_id,
        }

        self._json_id += 1

        return paylaod
