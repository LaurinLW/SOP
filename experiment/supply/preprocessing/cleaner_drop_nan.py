import pandas as pd

from experiment.supply.preprocessing.cleaner import Cleaner


class DropNaNCleaner(Cleaner):
    """Cleaner that drops all rows with a missing data point value within them from a data frama"""

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """method that drops all rows with a missing data point within them from a given DataFrame

        Args:
            data (pandas.DataFrame): DataFrame before being cleaned

        Returns:
            pandas.DataFrame: DataFrame after clean being cleaned
        """
        return data.dropna("index")
