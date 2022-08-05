import abc
import string


class MetricView(abc.ABC):
    """Base class for the visualization of metrics
    """

    @abc.abstractmethod
    def view(self, page: int = 0) -> string:
        """Returns HTML-Markup code for the requested page of the view
        """
        pass

    def get_pages(self) -> int:
        """Returns the maximum number of pages this view can produce
        """
        return 1
