from sop.metrics.views import MetricView
from enum import Enum
import numpy as np
from django.template.loader import render_to_string


class GraphType(Enum):
    BARGRAPH = 'Bargraph.html'
    LINEGRAPH = 'Linegraph.html'


class GraphView(MetricView):
    __type: GraphType
    __data: np.array

    def __init__(self, type: GraphType, data: np.array):
        """Constructor method. Creates a new GraphView

        Args:
            type: the type of graph that should be returned
            data: The data of the graph. the array has to have the shape (N, 2)
                  The first value is the x-value (or label in bargraphs) and the second value the y-value
        """
        self.__type = type

        if len(data.shape) != 2 or data.shape[1] != 2:
            raise TypeError("data has to be numpy array with the shape (N, 2)")
        self.__data = data

    def view(self, page: int = 0) -> str:
        return render_to_string(self.__type.value, {"x": self.__data[:, 0], "y": self.__data[:, 1], "name": "Metrik"})
