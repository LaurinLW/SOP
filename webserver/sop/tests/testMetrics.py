from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.base import File
from sop.models import ExperimentModel, VersionModel, DatasetModel, AlgorithmModel, ResultModel
from sop.metrics import TestMetric, AlgoMetric
from sop.metrics.views import ErrorView, TableView, GraphType, GraphView
import json
import os


class TestMetrics(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")

        self.d = DatasetModel()
        self.d.file.save('dataset.csv', File(open(os.path.join(os.getcwd(), 'sop/tests/testfiles/network_intrusions_short.csv'))))
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
        self.r = ResultModel(version=self.v)
        self.r.resultFile.save("test_save_file_2.csv", File(open(os.path.join(os.getcwd(), "sop/tests/testfiles/subspace_result0_test.csv"))))

        self.d2 = DatasetModel()
        self.d2.file.save('dataset2.csv', File(open(os.path.join(os.getcwd(), 'sop/tests/testfiles/canada_short.csv'))))
        self.d2.save()
        self.e2 = ExperimentModel(name="test", creator=self.user, latestVersion="1.0", latestStatus="paused", dataset=self.d2)
        self.e2.save()
        self.v2 = VersionModel(edits=1, runs=0, seed=1, status="running", numberSubspaces=1, minDimension=1, maxDimension=1, progress=0, experiment=self.e2)
        self.v2.save()
        self.v2.algorithms.add(AlgorithmModel.objects.get(name="abod"))
        self.v2.parameterSettings = json.dumps({"pyod.models.abod.ABOD": {
            "ID": AlgorithmModel.objects.get(name="abod").pk,
            "contamination": 0.1,
            "n_neighbors": 5,
            "method": "fast"
        }})
        self.v2.save()
        self.r2 = ResultModel(version=self.v2)
        self.r2.resultFile.save("test_save_file_2.csv", File(open(os.path.join(os.getcwd(), "sop/tests/testfiles/result_canada.csv"))))
        self.r2.save()

        self.m = TestMetric(self.v)

    def tearDown(self):
        pass

    def test_Unknown_Argument(self):
        self.m.filter('select= protocol_type;argument=value')
        self.assertEqual(type(self.m.view), ErrorView)
        self.assertEqual(self.m.view.msg, "Unknown argument: argument")

    def test_Trailing_Semicolon(self):
        self.m.filter('select=protocol_type;')
        self.assertEqual(type(self.m.view), TableView)

    def test_Space_In_Filter(self):
        self.m.filter('select = protocol_type')
        self.assertEqual(type(self.m.view), TableView)

    def test_Unknown_Column(self):
        self.m.filter('select=E')
        self.assertEqual(type(self.m.view), ErrorView)

    def test_Threshold_Type(self):
        self.m.filter('threshold=a')
        self.assertEqual(type(self.m.view), ErrorView)
        self.assertEqual(self.m.view.msg, 'Threshold value is not a float')

    def test_Wrong_Query(self):
        self.m.filter('query=protocol_type>a')
        self.assertEqual(type(self.m.view), ErrorView)

    def test_AlgoMetric(self):
        m = AlgoMetric(self.v)
        self.assertEqual(type(m.view), GraphView)
        self.assertEqual(m.view._GraphView__type, GraphType.BARGRAPH)

    def test_No_Index(self):
        m = TestMetric(self.v2)
        m.filter()
        self.assertEqual(type(m.view), TableView)
