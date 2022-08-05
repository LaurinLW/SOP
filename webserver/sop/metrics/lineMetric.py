from sop.metrics import Metric
import string
from sop.models import VersionModel
from sop.metrics.views import GraphView, GraphType
import numpy as np


class LineMetric(Metric):
    """An example metric to present the LINEGRAPH GraphType
    """

    def __init__(self, version: VersionModel) -> None:
        self._view = GraphView(GraphType.LINEGRAPH, np.array([[1, 2], [3, 4], [5, 6]]))

    def filter(self, filterString: string) -> None:
        pass
