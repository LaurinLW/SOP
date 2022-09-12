import numpy as np
import math

from pandas import DataFrame
from random import Random

from experiment.supply.preprocessing.cleaner import Cleaner
from experiment.supply.preprocessing.encoder import Encoder
from experiment.supply.subspace.invalid_number_subspaces_requested_exception import (
    InvalidNumberSubspacesRequestedException,
)
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
        self.__random_instance: Random = Random()
        self.__random_instance.seed(seed)
        self.__cleaned_data: DataFrame = cleaner.clean(data)

        self.__encoder: Encoder = encoder
        self.__quantity_created_subspaces: int = 0
        self.__amount_cleaned_data_columns: int = len(self.__cleaned_data.columns)

        self.__min_dimension = min(min_dimension, self.__amount_cleaned_data_columns)
        self.__max_dimension = min(max_dimension + 1, self.__amount_cleaned_data_columns + 1)

        self.__created_subspaces_dimensions: dict[int, list[list[int]]] = dict()  # {(i, list()) for i in range(self.__min_dimension, self.__max_dimension)}
        for i in range(self.__min_dimension, self.__max_dimension):
            self.__created_subspaces_dimensions[i] = list()
        self.__possibilites_for_dimension: list[
            list[int]
        ] = self.__calculate_possibilites_for_dimension_entry()
        self.__max_number_subspaces = 0
        for p in self.__possibilites_for_dimension:
            self.__max_number_subspaces += p[1]

    def __next__(self) -> Subspace:
        """creates a new Subspace and returns it

        Raises:
            StopIteration: when the numbers of wanted Subspaces is reached and another one is requested

        Returns:
            Subspace: returns the newly created Subspace
        """
        if self.__quantity_created_subspaces < self.__number_subspaces:
            subspace_index: np.ndarray = self.__cleaned_data.index.to_numpy()
            try:
                subspace_dimensions = self.__create_unique_subspace_dimensions()
            except InvalidNumberSubspacesRequestedException as e:
                raise e
            subspace_encoded: DataFrame = self.__encoder.encode(
                self.__cleaned_data.iloc[:, subspace_dimensions]
            )
            subspace_dimensions_names: str = list(subspace_encoded.columns)
            subspace_array: np.ndarray = subspace_encoded.to_numpy()
            self.__quantity_created_subspaces += 1
            return Subspace(subspace_array, subspace_dimensions_names, subspace_index)
        raise StopIteration

    def __create_unique_subspace_dimensions(self) -> list[int]:
        if not self.__possibilites_for_dimension:
            raise InvalidNumberSubspacesRequestedException

        chosen_dimension_indice: int = self.__random_instance.randint(
            0, len(self.__possibilites_for_dimension) - 1
        )

        chosen_dimension: list[int] = self.__possibilites_for_dimension[
            chosen_dimension_indice
        ]

        chosen_dimension[1] -= 1

        if chosen_dimension[1] == 0:
            self.__possibilites_for_dimension.remove(chosen_dimension)

        amount_dimensions: int = chosen_dimension[0]

        while True:
            subspace_dimensions: list[int] = self.__random_instance.sample(
                range(0, len(self.__cleaned_data.columns)), amount_dimensions
            )
            subspace_dimensions.sort()
            if subspace_dimensions not in self.__created_subspaces_dimensions[amount_dimensions]:
                self.__created_subspaces_dimensions[amount_dimensions].append(subspace_dimensions)
                return subspace_dimensions

    def __calculate_possibilites_for_dimension_entry(self) -> list[list[int]]:
        output: list[list[int]] = list()
        for i in range(self.__min_dimension, self.__max_dimension):
            possibilites_for_dimension_entry: list[int] = list()
            possibilites_for_dimension_entry.append(i)
            possibilites_for_dimension_entry.append(
                math.comb(self.__amount_cleaned_data_columns, i)
            )
            output.append(possibilites_for_dimension_entry)
        return output

    def __iter__(self) -> object:
        """returns itself to be iterable

        Returns:
            object: returns itself to be iterable
        """
        return self

    def get_max_number_subspaces(self) -> int:
        return self.__max_number_subspaces
