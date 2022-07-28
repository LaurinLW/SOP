import abc

from abc import ABC


class ParameterParser(ABC):
    """abstract class which all parameter parsers inherit from"""

    @abc.abstractmethod
    def get_parameters(self, model: str) -> dict:
        """returns parameters of the wanted model

        Args:
            parameter (str): model name of the parameters needed

        Returns:
            dict: a dictionary with the parameters of the wanted model
        """
        pass
