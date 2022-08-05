from sop.metrics import Metric
import string
from sop.models import VersionModel
from sop.metrics.views import GraphView, GraphType
import numpy as np


class AlgoMetric(Metric):
    """a metric that shows the number of selected algorithms for each category
    """

    def __init__(self, version: VersionModel) -> None:
        """constructor method. all computation is done
        """

        types = ["Probabilistic", "Linear Model", "Proximity-Based", "Outlier Ensembles", "Neural Networks", "Other"]
        data = np.empty((0, 2))
        for t in types:
            algos = version.algorithms.filter(category=t).count()
            data = np.append(data, [[t, algos]], axis=0)

        self._view = GraphView(GraphType.BARGRAPH, data)

    def filter(self, filterString: string) -> None:
        """this method does nothing because this metric does not provide filtering capability
        """
        pass
