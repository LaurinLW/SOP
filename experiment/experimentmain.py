import argparse
import sys
import os
import pandas as pd
from experiment.supply.job_supplier import JobSupplier
import threading
import queue
from experiment.supply.parser.parameter_parser_json import JsonParameterParser
from experiment.run.runner import Runner
from experiment.run.serial import Serial
import experiment.export.exporter as ex
import experiment.export.csvexporter as csvex
import experiment.progresscontrol as pc
from experiment.connection.rpcserverconnection import RPCServerConnection
from experiment.connection.serverconnection import ServerConnection
from experiment.run.parallel import Parallel
import signal
import json
import time


class Experiment:
    model_dir = "algorithms"
    model_file = "algorithms.txt"
    param_file = "parameters.json"

    def __init__(
        self,
        path_working_directory: str,
        seed: int,
        min_subspace_dim: int,
        max_subspace_dim: int,
        num_subspace: int,
        experiment_id: str,
        connection: str,
        debug: bool,
        processes: int = 1
    ) -> None:
        """constructor

        Args:
            path_working_directory (str): path to working directory
            seed (int): seed for rng
            min_subspace_dim (int): minimal subspace dimension
            max_subspace_dim (int): maximal subspace dimension
            num_subspace (int): number of subspaces that should be generated
            experiment_id (str): unique identifier for the experiment
            connection (str): string that allows to establish a connection to the server
            debug (bool): if true redirects all server messages to the console
            processes (int): number of processes used for parallel execution
        """

        server_connection: ServerConnection
        if debug:
            server_connection = _DebugServerConnection(connection, experiment_id)
        else:
            server_connection: ServerConnection = RPCServerConnection(connection, experiment_id)

        self._check_args(min_subspace_dim, max_subspace_dim, num_subspace, path_working_directory, server_connection)
        # signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._stop_signal)
        signal.signal(signal.SIGTERM, self._stop_signal)

        self._stop: threading.Event = threading.Event()
        # queue size should avoid loading to many subspaces into memory
        self._q_supply_run: queue.Queue = queue.Queue(2 * num_subspace)
        self._q_run_export: queue.Queue = queue.Queue()

        self._export_dir = "export"

        data_file: str
        for f in os.listdir(path_working_directory):
            if f.endswith(".csv"):
                data_file = f

        param_file = open(os.path.join(path_working_directory, Experiment.model_dir, Experiment.param_file), "r")

        param_file.seek(0)

        models: list[str] = json.load(param_file).keys()

        param_file.seek(0, 0)

        try:
            parameters: JsonParameterParser = JsonParameterParser(param_file)
        except Exception as e:
            self._output_error(str(e), server_connection)
            exit(1)

        self._progress: pc.ProgressControl = pc.ProgressControl(self, len(models), num_subspace, server_connection)

        self._supply: JobSupplier = JobSupplier(num_subspace,
                                                min_subspace_dim,
                                                max_subspace_dim,
                                                seed,
                                                pd.read_csv(os.path.join(path_working_directory, data_file)),
                                                models,
                                                parameters,
                                                self._q_supply_run,
                                                self._stop)
        if(processes <= 1):
            self._run: Runner = Serial(self._q_supply_run, self._q_run_export, self._stop)
        else:
            count = min(os.cpu_count(), processes)
            self._run: Runner = Parallel(self._q_supply_run, self._q_run_export, self._stop, count)

        export_path = os.path.join(path_working_directory, self._export_dir)
        if not os.path.exists(export_path):
            os.mkdir(export_path)

        self._export: ex.Exporter = csvex.CSVExporter(self._progress, self._q_run_export, self._stop, export_path)

        self._supply.start()
        self._run.start()
        self._export.start()

        check_interval: int = 30
        while not self._stop.is_set():
            if not self._supply.is_alive():
                self._output_error("The supply stage has crashed", server_connection)
                self.stop()
                break
            if not self._run.is_alive():
                self._output_error("The run stage has crashed", server_connection)
                self.stop()
                break
            if not self._export.is_alive():
                self._output_error("The export stage has crashed", server_connection)
                self.stop()
                break

            time.sleep(check_interval)

        self._supply.join()
        self._run.join()
        self._export.join()

    def stop(self) -> None:
        """This method signals to pipeline stages that they should clean up and terminate."""
        self._stop.set()

    def _stop_signal(self, sig, frame) -> None:
        self.stop()

    def _output_error(self, error: str, connection: ServerConnection):
        connection.send_error(error)
        print(error, file=sys.stderr)

    def _check_args(self, minsd: int, maxsd: int, ns: int, d: str, connection: ServerConnection):
        """Function that validates arguments. Shuts the program down in case of invalid arguments.

        Args:
            minsd (int): minimal subspace dimension
            maxsd (int): maximal subspace dimension
            ns (int): number of subspaces
            d (str): directory with all necessary files and subdirectories
            connection (ServerConnection): a server connection object to notify the server of errors
        """
        if minsd > maxsd:
            error = f"minsd may not be smaller than maxsd: {args.minsd} > {args.maxsd}"
            self._output_error(error, connection)
            exit(1)

        if ns <= 0:
            self._output_error("ns must be at least 1", connection)
            exit(1)

        if not os.path.isdir(d):
            self._output_error(f"directory {args.d} does not exist", connection)
            exit(1)

        model_dir = os.path.join(args.d, Experiment.model_dir)

        if not os.path.isdir(model_dir):
            self._output_error(f"the working directory does not contain the required {Experiment.model_dir} directory", connection)
            exit(1)

        param_flag: bool = False

        for f in os.listdir(model_dir):
            if f == Experiment.param_file:
                param_flag = True
                break

        if not param_flag:
            self._output_error(f"{Experiment.param_file} is missing in {model_dir}", connection)
            exit(1)

        data_flag: bool = False
        for f in os.listdir(d):
            if f.endswith(".csv"):
                data_flag = True
                break

        if not data_flag:
            self._output_error(f"data csv file is missing in {args.d}", connection)
            exit(1)


class _DebugServerConnection(ServerConnection):

    def send_progress(self, progress: int):
        print("Progress: ", progress)

    def send_error(self, error: str):
        print("ERROR: ", error)

    def send_warning(self, warning):
        print("WARNING: ", warning)

    def send_result(self, name: str):
        print("Finished Result: ", name)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="This Program runs an experiment.")
    parser.add_argument("-d", type=str, help="Working directory with all files relevant to the experiment.", required=True)
    parser.add_argument("-s", type=int, help="seed for rng", required=True)
    parser.add_argument("-minsd", type=int, help="minimal subspace dimension", required=True)
    parser.add_argument("-maxsd", type=int, help="maximal subspace dimension", required=True)
    parser.add_argument("-ns", type=int, help="number of subspaces", required=True)
    parser.add_argument("-id", type=str, help="unique identifier of the experiment", required=True)
    parser.add_argument("-c", type=str, help="server url", required=True)
    parser.add_argument("-p", type=int, help="number of processes for parallel execution, default 1")
    parser.add_argument("-debug", help="enables debug mode, redirects server messages to console", action="store_true")

    args: argparse.Namespace = parser.parse_args()
    if args.p is None:
        p_count = 1
    else:
        p_count = args.p
    Experiment(args.d, args.s, args.minsd, args.maxsd, args.ns, args.id, args.c, args.debug, p_count)
