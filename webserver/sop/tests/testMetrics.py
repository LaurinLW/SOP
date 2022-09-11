from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.base import File
from sop.models import ExperimentModel, VersionModel, DatasetModel, AlgorithmModel
from sop.metrics import TestMetric, AlgoMetric
from sop.metrics.views import ErrorView, TableView, GraphType, GraphView
import numpy as np
import pandas as pd
import json


class TestMetrics(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        df = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list('ABCD'))
        df.to_csv('dataset.csv')

        self.d = DatasetModel()
        self.d.file.save('dataset.csv', File(open('dataset.csv')))
        self.d.save()
        self.e = ExperimentModel(name="test", creator=self.user, latestVersion="1.0", latestStatus="paused", dataset=self.d)
        self.e.save()
        self.v = VersionModel(edits=1, runs=0, seed=1, status="running", numberSubspaces=1, minDimension=1, maxDimension=1, progress=0, experiment=self.e)
        self.v.save()
        self.v.algorithms.add(AlgorithmModel.objects.get(name="abod"))
        self.v.parameterSettings = json.dumps({"pyod.models.abod.ABOD": {
            "ID": AlgorithmModel.objects.get(name="abod").pk,
            "contamination": 0.1,
            "n_neighbors": 5,
            "method": "fast"
        }})
        self.v.save()
        self.m = TestMetric(self.v)

    def tearDown(self):
        pass

    def test_Unknown_Argument(self):
        self.m.filter('select= A;argument=value')
        self.assertEqual(type(self.m.view), ErrorView)
        self.assertEqual(self.m.view.msg, "Unknown argument: argument")

    def test_Trailing_Semicolon(self):
        self.m.filter('select=A;')
        self.assertEqual(type(self.m.view), TableView)

    def test_Space_In_Filter(self):
        self.m.filter('select = A')
        self.assertEqual(type(self.m.view), TableView)

    def test_Unknown_Column(self):
        self.m.filter('select=E')
        self.assertEqual(type(self.m.view), ErrorView)

    def test_Threshold_Type(self):
        self.m.filter('threshold=a')
        self.assertEqual(type(self.m.view), ErrorView)
        self.assertEqual(self.m.view.msg, 'Threshold value is not a float')

    def test_Wrong_Query(self):
        self.m.filter('query=A>a')
        self.assertEqual(type(self.m.view), ErrorView)

    def test_AlgoMetric(self):
        m = AlgoMetric(self.v)
        self.assertEqual(type(m.view), GraphView)
        self.assertEqual(m.view._GraphView__type, GraphType.BARGRAPH)
