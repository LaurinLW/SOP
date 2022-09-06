from django.test import TestCase, Client
from django.contrib.auth.models import User
from sop.models import DatasetModel, ExperimentModel, VersionModel


class TestDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        self.d = DatasetModel()
        self.d.save()
        self.e = ExperimentModel(name="test", creator=self.user, latestVersion="1.0", latestStatus="running", dataset=self.d)
        self.e.save()
        self.v = VersionModel(edits=1, runs=0, seed=1, status="running", numberSubspaces=1, minDimension=1, maxDimension=1, progress=0, experiment=self.e)
        self.v.save()

    def test_Ajax(self):
        c = Client()
        c.post("/login", {'username': 'test', 'password': 'testpasw'})
        json_response = c.get("/details/1/1.0", **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}).json()
        assert json_response == {'update_progress': '0', 'update_status': 'running'}
