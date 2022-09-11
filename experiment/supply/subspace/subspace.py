import numpy as np


class Subspace:
    """Represents a Subspace that models are trained on"""

    def __init__(
        self,
        subspace_data: np.ndarray,
        subspace_dimensions: list[str],
        indexes_after_clean: np.ndarray,
    ) -> None:
        """constructor method that creates a Subspace

        Args:
            subspace_data (np.array): data of the subspace
            subspace_dimensions (list[str]): name of the dimensions of the subspace
        """
        self.__data: np.ndarray = subspace_data
        self.__dimensions: list[str] = subspace_dimensions
        self.__indexes_after_cleaning: np.ndarray = indexes_after_clean

    @property
    def data(self) -> np.ndarray:
        return self.__data

    @property
    def dimensions(self) -> list[str]:
        return self.__dimensions

    @property
    def indexes_after_clean(self) -> np.ndarray:
        return self.__indexes_after_cleaning

    @data.setter
    def data(self, value):
        """Does not change value. Data may not be altered after creation."""
        pass

    @dimensions.setter
    def dimensions(self, value):
        """Does not change value. Dimensions may not be altered after creation."""
        pass
