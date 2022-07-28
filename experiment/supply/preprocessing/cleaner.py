import abc
import pandas

from abc import ABC


class Cleaner(ABC):
    """abstract class Cleaner which cleans DataFrames from NaN values by following specific strategies"""

    @abc.abstractmethod
    def clean(self, data: pandas.DataFrame) -> pandas.DataFrame:
        """abstract method that cleans a given DataFrame from missing values by following specific strategies

        Args:
            data (pandas.DataFrame): DataFrame before clean

        Returns:
            pandas.DataFrame: DataFrame after clean
        """
        pass
