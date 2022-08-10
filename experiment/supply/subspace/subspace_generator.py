import numpy as np

from pandas import DataFrame
from random import Random

from experiment.supply.preprocessing.cleaner import Cleaner
from experiment.supply.preprocessing.encoder import Encoder
from experiment.supply.subspace.subspace import Subspace


class SubspaceGenerator:
    """class implemented as an lazy Iterator that generates subspaces"""

    def __init__(
        self,
        number_subspaces: int,
        min_dimension: int,
        max_dimension: int,
        seed: int,
        data: DataFrame,
        encoder: Encoder,
        cleaner: Cleaner,
    ) -> None:
        """constructor method that creates an SubspaceGenerator

        Args:
            number_subspaces (int): numbers of suspaces to create
            min_dimension (int): min amount of dimensions of the subspace
            max_dimension (int): max amount of dimensions of the subspace
            seed (int): seed for random numbers
            data (DataFrame): DataFrame which to create Subspaces from
            encoder (Encoder): Encoder to encode the categorical of the DataFrame with
            cleaner (Cleaner): Cleaner to handle missing values in the DataFrame with
        """

        self.__number_subspaces: int = number_subspaces
        self.__min_dimension: int = min_dimension
        self.__max_dimension: int = max_dimension + 1
        self.__random_instance: Random = Random()
        self.__random_instance.seed(seed)
        self.__cleanedData: DataFrame = cleaner.clean(data)
        self.__encoder: Encoder = encoder
        self.__quantity_created_subspaces: int = 0
        self.created_subspaces_dimensions: list[list[int]] = list()

    def __next__(self) -> Subspace:
        """creates a new Subspace and returns it

        Raises:
            StopIteration: when the numbers of wanted Subspaces was reached and another one is requested

        Returns:
            Subspace: returns the created Subspace
        """
        if self.__quantity_created_subspaces < self.__number_subspaces:
            subspace_index: np.ndarray = self.__cleanedData.index.to_numpy()
            subspace_dimensions = self.__create_unique_subspace_dimensions()
            self.created_subspaces_dimensions.append(subspace_dimensions)
            subspace_encoded: DataFrame = self.__encoder.encode(
                self.__cleanedData.iloc[:, subspace_dimensions]
            )
            subspace_dimensions_names: str = list(subspace_encoded.columns)
            subspace_array: np.ndarray = subspace_encoded.to_numpy()
            self.__quantity_created_subspaces += 1
            return Subspace(subspace_array, subspace_dimensions_names, subspace_index)
        raise StopIteration

    def __create_unique_subspace_dimensions(self) -> list[int]:
        while True:
            amount_dimensions: int = self.__random_instance.randrange(
                self.__min_dimension, self.__max_dimension
            )
            subspace_dimensions: list[int] = self.__random_instance.sample(
                range(0, len(self.__cleanedData.columns)), amount_dimensions
            )
            subspace_dimensions.sort()
            if subspace_dimensions not in self.created_subspaces_dimensions:
                return subspace_dimensions

    def __iter__(self) -> object:
        """returns itself to be iterable

        Returns:
            object: returns itself to be iterable
        """
        return self
