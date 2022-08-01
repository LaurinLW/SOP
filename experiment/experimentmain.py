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
import signal


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
        """
        # signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        self._stop: threading.Event = threading.Event()
        # queue size should avoid loading to many subspaces into memory
        self._q_supply_run: queue.Queue = queue.Queue(2*num_subspace)
        self._q_run_export: queue.Queue = queue.Queue()

        self._export_dir = "export"

        data_file: str
        for f in os.listdir(path_working_directory):
            if f.endswith(".csv"):
                data_file = f
        model_file = open(os.path.join(path_working_directory, Experiment.model_dir, Experiment.model_file), "r")
        models: list[str] = model_file.readlines()
        model_file.close()

        server_connection: ServerConnection = RPCServerConnection(connection, experiment_id)

        self._progress: pc.ProgressControl = pc.ProgressControl(self, len(models), num_subspace, server_connection)

        parameters: JsonParameterParser = JsonParameterParser(open(os.path.join(path_working_directory,
                                                                                Experiment.model_dir,
                                                                                Experiment.param_file), "r"))

        self._supply: JobSupplier = JobSupplier(num_subspace,
                                                min_subspace_dim,
                                                max_subspace_dim,
                                                seed,
                                                pd.read_csv(os.path.join(path_working_directory, data_file)),
                                                models,
                                                parameters,
                                                self._q_supply_run,
                                                self._stop)

        self._run: Runner = Serial(self._q_supply_run, self._q_run_export, self._stop)

        export_path = os.path.join(path_working_directory, self._export_dir)
        os.mkdir(export_path)

        self._export: ex.Exporter = csvex.CSVExporter(self._progress, self._q_run_export, self._stop, export_path)

        self._supply.start()
        self._run.start()
        self._export.start()

        self._supply.join()
        self._run.join()
        self._export.join()

    def stop(self) -> None:
        """This method signals to pipeline stages that they should clean up and terminate."""
        self._stop.set()


def _check_args(args: argparse.Namespace):
    """Checks whether the arguments are usable

    Args:
        args (argparse.Namespace): arguments
    """
    if args.minsd > args.maxsd:
        print(f"minsd may not be smaller than maxsd: {args.minsd} > {args.maxsd}", file=sys.stderr)
        exit(1)

    if args.ns <= 0:
        print("ns must be at least 1", file=sys.stderr)
        exit(1)

    if not os.path.isdir(args.d):
        print(f"directory {args.d} does not exist", file=sys.stderr)
        exit(1)

    model_dir = os.path.join(args.d, Experiment.model_dir)

    if not os.path.isdir(model_dir):
        print(f"the working directory does not contain the required {Experiment.model_dir} directory", file=sys.stderr)
        exit(1)

    algo_flag: bool = False
    param_flag: bool = False

    for f in os.listdir(model_dir):
        if f == Experiment.model_file:
            algo_flag = True
        if f == Experiment.param_file:
            param_flag = True

    if not algo_flag:
        print(f"{Experiment.model_file} is missing in {model_dir}", file=sys.stderr)
        exit(1)

    if not param_flag:
        print(f"{Experiment.param_file} is missing in {model_dir}", file=sys.stderr)
        exit(1)

    data_flag: bool = False
    for f in os.listdir(args.d):
        if f.endswith(".csv"):
            data_flag = True

    if not data_flag:
        print(f"data csv file is missing in {args.d}", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="This Program runs an experiment.")
    parser.add_argument("-d", type=str, help="Working directory with all files relevant to the experiment.", required=True)
    parser.add_argument("-s", type=int, help="seed for rng", required=True)
    parser.add_argument("-minsd", type=int, help="minimal subspace dimension", required=True)
    parser.add_argument("-maxsd", type=int, help="maximal subspace dimension", required=True)
    parser.add_argument("-ns", type=int, help="number of subspaces", required=True)
    parser.add_argument("-id", type=str, help="unique identifier of the experiment", required=True)
    parser.add_argument("-c", type=str, help="server url", required=True)

    args: argparse.Namespace = parser.parse_args()
    _check_args(args)
    Experiment(args.d, args.s, args.minsd, args.maxsd, args.ns, args.id, args.c)