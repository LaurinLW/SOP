from typing import TextIO
import unittest
import os

from experiment.supply.parser.parameter_parser_json import JsonParameterParser


class ParameterParserJsonTest(unittest.TestCase):
    def setUp(self) -> None:
        test_dir = (os.path.sep).join((__file__.split(".")[0]).split(os.path.sep)[0:-1])
        self.input_json_file: TextIO = open(os.path.join(test_dir, "test_resources", "parser_test_json.json"), "r")
        self.solution: dict = {
            "title": "Sample Konfabulator Widget",
            "name": "main_window",
            "width": 500,
            "height": 500,
        }
        self.parser: JsonParameterParser = JsonParameterParser(self.input_json_file)

    def test_get_parameters(self) -> None:
        self.assertTrue(self.parser.get_parameters("window") == self.solution)

    def test_get_parameters_wrong_key(self) -> None:
        self.assertTrue(self.parser.get_parameters("test") == dict())
