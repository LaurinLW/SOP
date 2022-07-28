class Experiment:
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
        pass

    def stop(self) -> None:
        """This method signals to pipeline stages that they should clean up and terminate."""
        pass
