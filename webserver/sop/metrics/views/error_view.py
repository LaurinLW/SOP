from sop.metrics.views import MetricView
from django.template.loader import render_to_string


class ErrorView(MetricView):

    def __init__(self, error_msg: str):
        self.msg = error_msg

    def view(self, page: int = 0) -> str:
        return render_to_string("ErrorView.html", {"msg": self.msg})
