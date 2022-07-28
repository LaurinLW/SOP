import numpy as np


class Subspace:
    """Represents a Subspace that models are trained on
    """

    def __init__(self, subspace_data: np.ndarray, subspace_dimensions: list[str]) -> None:
        """constructor method that creates a Subspace

        Args:
            subspace_data (np.array): data of the subspace
            subspace_dimensions (list[str]): name of the dimensions of the subspace
        """
        self.__data: np.array = subspace_data
        self.__dimensions: list[str] = subspace_dimensions

    @property
    def data(self) -> np.ndarray:
        return self.__data

    @property
    def dimensions(self) -> list[str]:
        return self.__dimensions

    @data.setter
    def set__data(self):
        """Does not change value. Data may not be altered after creation.
        """
        pass

    @dimensions.setter
    def set__dimensions(self):
        """Does not change value. Dimensions may not be altered after creation.
        """
        pass
