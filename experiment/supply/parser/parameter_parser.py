import abc

from abc import ABC
from typing import TextIO


class ParameterParser(ABC):
    """abstract class which all parameter parsers inherit from"""

    @abc.abstractmethod
    def get_parameters(self, parameterFile: TextIO) -> dict:
        """returns parameters of the wanted model

        Args:
            parameter (str): model name of the parameters needed

        Returns:
            dict: a dictionary with the parameters of the wanted model
        """
        pass
