import unittest

from pandas import DataFrame

from experiment.supply.preprocessing.encoder import Encoder
from experiment.supply.preprocessing.encoder_one_hot import EncoderOneHot


class EncoderOneHotTest(unittest.TestCase):
    def setUp(self) -> None:
        self.encoder: Encoder = EncoderOneHot()
        self.testDataFrame: DataFrame = DataFrame(
            {"Stadt": ["Stuttgart", "Berlin", "Hamburg"], "Geld": [10, 180, 360]}
        )
        self.testSolution: DataFrame = DataFrame(
            {
                "Stadt_Stuttgart": [1, 0, 0],
                "Stadt_Berlin": [0, 1, 0],
                "Stadt_Hamburg": [0, 0, 1],
                "Geld": [10, 180, 360],
            }
        )

    def test_encode_one_hot(self) -> None:
        self.assertTrue(
            DataFrame.equals(self.encoder.encode(self.testDataFrame), self.testSolution)
        )

    def test_encode_one_hot_no_categorical(self) -> None:
        self.assertTrue(
            DataFrame.equals(self.encoder.encode(self.testSolution), self.testSolution)
        )
