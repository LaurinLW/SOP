from sop.metrics import Metric
import string
from sop.models import VersionModel
from sop.metrics.views import TableView, ErrorView
import pandas as pd
import numpy as np
from sop.models import ResultModel
from django.db.models import Q
from pandas.core.computation.ops import UndefinedVariableError


class TestMetric(Metric):
    """A metric that calculates the amount of algorithms in each category that classify a datapoint as an outlier
    """
    def __init__(self, version: VersionModel) -> None:
        self._version = version
        self.filter()

    def filter(self, filterString: string = '') -> None:
        """Recalculates the metric using the filterstring

        Args:
            filterString: 3 options are provided:
                          - query: filter the dataset using pandas query function syntax
                          - threshold: set the quantile that is considered an outlier
                          - select: select only certain columns of the dataset, multiple columns must be separated by a comma
                          The whole filterString must have to following form:
                               option1=value1;option2=value2
                          An example would be select=column1,column2;threshold=0.99
        """

        dataset = pd.read_csv(self._version.experiment.dataset.file.path)
        dataset.rename(columns={'Unnamed: 0': 'index'}, inplace=True)

        # parse the filter string
        percentile = 0.95
        select = dataset.columns  # select all columns by default
        query = 'index==index'  # select all rows by default

        queries = filterString.split(';')
        for q in queries:
            s = q.split('=')
            argument = s[0].strip()
            if argument == 'threshold':
                try:
                    percentile = float(s[1].strip())
                except ValueError:
                    self._view = ErrorView('Threshold value is not a float')
                    return
                if percentile > 1 or percentile < 0:
                    self._view = ErrorView('Threshold has to be between 0 and 1')
                    return
            elif argument == 'select':
                select = ['index']
                columns = s[1].split(',')
                for c in columns:
                    select.append(c.strip())
            elif argument == 'query':
                query = s[1].strip()
            elif argument != '':
                self._view = ErrorView('Unknown argument: ' + argument)
                return

        try:
            dataset = dataset[select].query(query)
        except (ValueError, KeyError, UndefinedVariableError) as e:
            self._view = ErrorView(str(e))
            return

        # setup new columns for the algorithm categories
        types = ["Probabilistic", "Linear Model", "Proximity-Based", "Outlier Ensembles", "Neural Networks", "Other"]
        num_executions = dict()
        for t in types:
            algos = self._version.algorithms.filter(category=t).count()
            num_executions[t] = algos * self._version.numberSubspaces
        for t in types:
            dataset[t] = 0
        select = dataset.columns

        results = ResultModel.objects.filter(version=self._version)
        for r in results:
            resultData = pd.read_csv(r.resultFile.path)
            # only select columns with data from algorithms + the index
            indices = resultData['index']
            resultData = resultData[[c for c in resultData.columns if '(' in c]]
            resultData.columns = [s.split('(')[0]for s in resultData.columns]
            threshhold = resultData.quantile(percentile)
            resultData['index'] = indices

            dataset = dataset.join(resultData.set_index('index'), on='index', lsuffix='_', rsuffix='')

            for c in resultData.columns.drop('index'):
                algos = self._version.algorithms.filter(Q(class_name=c))
                if len(algos) != 1:
                    continue

                algo = algos[0]
                # add 1 in the right category when the outlier score is above the threshold
                dataset[algo.category] = dataset.apply(lambda x: x[algo.category] + 1 if x[c] is not None and  # noqa: E127
                                                                                         x[c] is not np.nan and  # noqa: E127
                                                                                         x[c] >= threshhold[c]  # noqa: E127
                                                                                      else x[algo.category], axis=1)  # noqa: E127

            dataset = dataset[select]

        for t in types:
            dataset[t] = dataset[t].apply(lambda x: str(x) + '/' + str(num_executions[t]))

        self._view = TableView(dataset.columns, dataset.to_numpy())
