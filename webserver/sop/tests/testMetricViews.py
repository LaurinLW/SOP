from django.test import TestCase
from sop.metrics.views import TableView, ErrorView, GraphType, GraphView
import numpy as np
import pandas as pd


class TestMetricViews(TestCase):

    def setUp(self):
        TableView.PAGE_SIZE = 2
        df = pd.DataFrame(np.arange(0, 99), columns=list('A'))
        self.columns = df.columns
        self.data = df.to_numpy()

    def tearDown(self):
        pass

    def test_Max_Pages(self):
        view = TableView(self.columns, self.data)
        assert view.get_pages() == 50

    def test_Pagination(self):
        view = TableView(self.columns, self.data)
        self.assertHTMLEqual(view.view(0), """<div style="overflow: scroll;width: 100%;height: 100%;">
                                                   <table cellspacing="0" cellpadding="0"><tr>
                                                   <th style="padding: 0px 10px 0px 10px;border-right: solid 1px #fff;">A</th></tr>
                                                   <tr><td style="padding: 0px 10px 0px 10px;border-right: solid 1px #fff;">0</td></tr>
                                                   <tr><td style="padding: 0px 10px 0px 10px;border-right: solid 1px #fff;">1</td></tr></table></div>""")
        self.assertHTMLEqual(view.view(1), """<div style="overflow: scroll;width: 100%;height: 100%;">
                                                   <table cellspacing="0" cellpadding="0"><tr>
                                                   <th style="padding: 0px 10px 0px 10px;border-right: solid 1px #fff;">A</th></tr>
                                                   <tr><td style="padding: 0px 10px 0px 10px;border-right: solid 1px #fff;">2</td></tr>
                                                   <tr><td style="padding: 0px 10px 0px 10px;border-right: solid 1px #fff;">3</td></tr></table></div>""")
        self.assertHTMLEqual(view.view(49), """<div style="overflow: scroll;width: 100%;height: 100%;">
                                                    <table cellspacing="0" cellpadding="0"><tr>
                                                    <th style="padding: 0px 10px 0px 10px;border-right: solid 1px #fff;">A</th>
                                                    </tr><tr><td style="padding: 0px 10px 0px 10px;border-right: solid 1px #fff;">98</td></tr></table></div>""")

    def test_ErrorView(self):
        e = ErrorView("string that contains the error")
        self.assertEqual(e.view(), '<p style="color: red;">Error: string that contains the error</p>')

    def test_GraphView_Max_Pages(self):
        df = pd.DataFrame(np.random.randint(0, 100, size=(100, 2)), columns=list('AB'))
        data = df.to_numpy()
        view = GraphView(GraphType.BARGRAPH, data)

        self.assertEqual(view.get_pages(), 1)
