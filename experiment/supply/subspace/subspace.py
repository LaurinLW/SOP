import numpy as np


class Subspace:
    """Represents Subspaces that models are trained on
    """

    def __init__(self, subspace_data: np.ndarray, subspace_dimensions: list[str]) -> None:
        """_summary_

        Args:
            subspace_data (np.array): data of the subspace
            subspace_dimensions (list[str]): name of the dimensions of the subspace
        """
        self._data: np.array = subspace_data
        self._dimensions: list[str] = subspace_dimensions

    @property
    def data(self) -> np.ndarray:
        return self._data

    @property
    def dimensions(self):
        return self._dimensions

    @data.setter
    def set_data(self):
        """Does not change value. Data may not be altered after creation.
        """
        pass

    @dimensions.setter
    def set_dimensions(self):
        """Does not change value. Dimensions may not be altered after creation.
        """
        pass
