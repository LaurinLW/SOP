from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from sop.models import ExperimentModel, VersionModel, ResultModel, DatasetModel
import requests
import shutil
import os
import pandas


class TestRPCEntryPoint(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        self.d = DatasetModel()
        self.d.save()
        self.e = ExperimentModel(name="test", creator=self.user, latestVersion="1.0", latestStatus="paused", dataset=self.d)
        self.e.save()
        self.v = VersionModel(edits=1, runs=0, seed=1, status="running", numberSubspaces=1, minDimension=1, maxDimension=1, progress=0, experiment=self.e)
        self.v.save()

    def testSendProgress(self):
        payload = {
            "method": "receiveProgress",
            "params": [1, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).progress, 1)

    def testSendProgress_100(self):
        payload = {
            "method": "receiveProgress",
            "params": [100, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).progress, 100)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).status, "finished")

    def testSendProgress_101(self):
        payload = {
            "method": "receiveProgress",
            "params": [101, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).progress, 0)

    def testSendProgress_Negative(self):
        payload = {
            "method": "receiveProgress",
            "params": [-1, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).progress, 0)

    def testSendProgress_Smaller(self):
        payload_one = {
            "method": "receiveProgress",
            "params": [10, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        payload_two = {
            "method": "receiveProgress",
            "params": [1, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload_one)
        requests.post(self.live_server_url + "/rpc", json=payload_two)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).progress, 10)

    def testSendProgress_After_Finished(self):
        payload_one = {
            "method": "receiveProgress",
            "params": [100, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        payload_two = {
            "method": "receiveProgress",
            "params": [1, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload_one)
        requests.post(self.live_server_url + "/rpc", json=payload_two)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).progress, 100)

    def testSendProgress_Not_Existing_Version(self):
        payload = {
            "method": "receiveProgress",
            "params": [1, 0],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).progress, 0)

    def testSendError(self):
        payload = {
            "method": "receiveError",
            "params": ["Error: test", self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).error, "Error: test")

    def testSendError_Not_Existing_Version(self):
        payload = {
            "method": "receiveError",
            "params": ["Error: test", 0],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(VersionModel.objects.get(pk=self.v.pk).error, None)

    def testSendResult_Not_Existing_Version(self):
        payload = {
            "method": "receiveResult",
            "params": ["testfile.csv", 0],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(ResultModel.objects.all().count(), 0)

    def testSendResult(self):
        if not os.path.exists(os.path.abspath(os.getcwd()) + "/experimente"):
            os.mkdir(os.path.abspath(os.getcwd()) + "/experimente")
        if not os.path.exists(os.path.abspath(os.getcwd()) + "/experimente/" + str(self.v.experiment.id) + ".1.0"):
            os.mkdir(os.path.abspath(os.getcwd()) + "/experimente/" + str(self.v.experiment.id) + ".1.0")
        if not os.path.exists(os.path.abspath(os.getcwd()) + "/experimente/" + str(self.v.experiment.id) + ".1.0/export"):
            os.mkdir(os.path.abspath(os.getcwd()) + "/experimente/" + str(self.v.experiment.id) + ".1.0/export")
        shutil.copyfile(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/subspace_result0_test.csv",
                        os.path.abspath(os.getcwd()) + "/experimente/" + str(self.v.experiment.id) + ".1.0/export/subspace_result0_test.csv")
        payload = {
            "method": "receiveResult",
            "params": ["subspace_result0_test.csv", self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload)
        self.assertEqual(ResultModel.objects.all().count(), 1)
        same = True
        for a in pandas.read_csv(ResultModel.objects.get(version=self.v).resultFile.path):
            if a not in pandas.read_csv(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/subspace_result0_test.csv"):
                same = False
        assert same
        payload_clean_up = {
            "method": "receiveProgress",
            "params": [100, self.v.id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        requests.post(self.live_server_url + "/rpc", json=payload_clean_up)
        os.remove(ResultModel.objects.get(version=self.v).resultFile.path)
