from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from sop.models import ExperimentModel, VersionModel, DatasetModel, AlgorithmModel
import os
from django.core.files.base import File
import json
import time
import docker
from docker.errors import ImageNotFound


class SeleniumTestStartView(LiveServerTestCase):
    def setUp(self):
        client = docker.from_env()
        try:
            client.images.get("sop-experiment")
        except ImageNotFound:
            try:
                nets = client.networks.list(names=["sop-network"])
                if len(nets) == 0:
                    client.networks.create("sop-network")
            except:
                pass
            try:
                client.volumes.create("sop-datasets")
            except:
                pass
            try:
                client.volumes.create("sop-algorithms")
            except:
                pass
            try:
                client.volumes.create("sop-results")
            except:
                pass
            client.images.build(
                path="..", dockerfile="Dockerfile_experiment", tag="sop-experiment"
            )

        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        self.d = DatasetModel(name="test", creator=self.user)
        self.d.file.save("file", File(open(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/network_intrusions_short.csv")))
        self.d.save()
        self.e = ExperimentModel(name="test", creator=self.user, latestVersion="1.0", latestStatus="paused", dataset=self.d)
        self.e.save()
        self.v = VersionModel(edits=1, runs=0, seed=1, status="paused", numberSubspaces=1, minDimension=1, maxDimension=1, progress=0, experiment=self.e)
        self.v.save()
        self.v.algorithms.add(AlgorithmModel.objects.get(name="abod"))
        self.v.parameterSettings = json.dumps({"pyod.models.abod.ABOD": {
            "ID": AlgorithmModel.objects.get(name="abod").pk,
            "contamination": 0.1,
            "n_neighbors": 5,
            "method": "fast"
        }})
        self.v.save()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.selenium = webdriver.Chrome(service=Service(ChromeDriverManager(version="105.0.5195.52").install()), options=chrome_options)
        self.selenium.implicitly_wait(10)
        self.selenium.get(self.live_server_url + "/login")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('testpasw')
        self.selenium.find_element(By.CLASS_NAME, 'login_button').click()
        self.selenium.get(self.live_server_url + "/details/" + str(self.e.pk) + "/1.0")

    def tearDown(self):
        self.selenium.quit()

    def test_Start(self):
        if not os.path.exists(os.path.abspath(os.getcwd()) + "/experimente"):
            os.mkdir(os.path.abspath(os.getcwd()) + "/experimente")
        with self.settings(RPC_PATH=f'{self.live_server_url}/rpc', SHARED_EXPERIMENT=f'{os.path.abspath(os.getcwd())}/experimente'):
            self.selenium.find_element(By.ID, 'start').click()
            time.sleep(2)
            assert self.selenium.find_element(By.ID, 'status').text == "Status: running"
            self.selenium.find_element(By.ID, 'stop').click()
