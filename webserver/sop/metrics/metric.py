import abc
import string
from sop.metrics.views.metricView import MetricView
from sop.models import VersionModel


class Metric(abc.ABC):
    """The baseclass for all metrics.
        The name of subclasses must only contain characters that are found in URLs.
        Subclasses must
    """

    @abc.abstractmethod
    def __init__(self, version: VersionModel) -> None:
        pass

    @abc.abstractmethod
    def filter(self, filterString: string) -> None:
        """ Allows the metric to be filtered.
            The semantic of the filter string is determined by the subclass
        """
        pass

    @property
    def view(self) -> MetricView:
        return self._view
