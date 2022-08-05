import string
from sop.metrics.views import MetricView
import numpy as np
from django.template.loader import render_to_string
from math import ceil


class TableView(MetricView):
    PAGE_SIZE = 50

    def __init__(self, columns: np.array, data: np.array):
        """Constructor method. Creates a new TableView

        Args:
            columns: labels for the table columns
            data: The data of the table. Must have the dimension (N, len(columns))
        """
        self.__columns = columns

        self.__data = data

    def view(self, page: int = 0) -> string:
        upper_end = min((page + 1) * TableView.PAGE_SIZE, len(self.__data))

        return render_to_string("TableView.html", {"columns": self.__columns,
                                                   "data": self.__data[page * TableView.PAGE_SIZE:upper_end]})

    def get_pages(self) -> int:
        return ceil(len(self.__data) / TableView.PAGE_SIZE)
