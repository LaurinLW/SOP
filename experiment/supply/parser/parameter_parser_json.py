import json
from typing import TextIO

from experiment.supply.parser.parameter_parser import ParameterParser


class JsonParameterParser(ParameterParser):
    """ParameterParser that parses json files"""

    def __init__(self, parameterFile: TextIO) -> None:
        """initializes an object of JsonParameterParser and transforms the given json  field to a dictionary

        Args:
            jsonFile (File): JSONField to parse
        """
        self.__jsonFile: dict = json.load(parameterFile)
        parameterFile.close()

    def get_parameters(self, model: str) -> dict:
        """returns the parameters of a given model String as a dictionary

        Args:
            model (str): the String name of the model which parameters are wanted

        Returns:
            dict: a dictionary with the parameters of the wanted model
        """
        output: dict = self.__jsonFile.get(model)
        if output is None:
            return dict()
        return output
