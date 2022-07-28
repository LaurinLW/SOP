import unittest

from django.forms import JSONField
from experiment.supply.parser.parameter_parser_json import JsonParameterParser


class ParameterParserJsonTest(unittest.TestCase):
    def setUp(self) -> None:
        self.input_json_file: JSONField = {
            "window": {
                "title": "Sample Konfabulator Widget",
                "name": "main_window",
                "width": 500,
                "height": 500,
            },
            "image": {
                "src": "Images/Sun.png",
                "name": "sun1",
                "hOffset": 250,
                "vOffset": 250,
                "alignment": "center",
            },
            "text": {
                "data": "Click Here",
                "size": 36,
                "style": "bold",
                "name": "text1",
                "hOffset": 250,
                "vOffset": 100,
                "alignment": "center",
                "onMouseUp": "sun1.opacity = (sun1.opacity / 100) * 90;",
            },
        }
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
