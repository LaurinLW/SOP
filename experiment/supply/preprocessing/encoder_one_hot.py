import category_encoders as ce
import pandas

from experiment.supply.preprocessing.encoder import Encoder


class EncoderOneHot(Encoder):
    """Encoder that uses the One Hot approach to change categorical data points to numerical data points in a DataFrame"""

    def __init__(self) -> None:
        """init method sets the CategoryEncoder OneHotEncoder as the encoder with category names on"""
        self.__encoder: ce.OneHotEncoder = ce.OneHotEncoder(use_cat_names=True)

    def encode(self, data: pandas.DataFrame) -> pandas.DataFrame:
        """encodes categorical data points of a DataFrame to numerical data points following the One Hot approach

        Args:
            data (pandas.DataFrame): DataFrame before being encoded

        Returns:
            pandas.Dataframe: DataFrame after being encoded
        """
        return self.__encoder.fit_transform(data)
