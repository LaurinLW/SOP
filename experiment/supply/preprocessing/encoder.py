import abc
import pandas

from abc import ABC


class Encoder(ABC):
    """abstract class which encodes categorical data from a data set to numerical values by following specific strategies"""

    @abc.abstractmethod
    def encode(self, data: pandas.DataFrame) -> pandas.DataFrame:
        """abstract method which encodes a given DataFrame by following specific strategies

        Args:
            data (pandas.DataFrame): DataFrame before being encoded

        Returns:
            pandas.DataFrame: DataFrame after being encoded
        """
        pass
