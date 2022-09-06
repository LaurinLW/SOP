from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from sop.models import ExperimentModel, VersionModel, DatasetModel


class SeleniumTestDeleteView(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        self.d = DatasetModel()
        self.d.save()
        self.e = ExperimentModel(name="test", creator=self.user, latestVersion="1.0", latestStatus="paused", dataset=self.d)
        self.e.save()
        self.v = VersionModel(edits=1, runs=0, seed=1, status="paused", numberSubspaces=1,
                              minDimension=1, maxDimension=1, progress=0, experiment=self.e, pid=None)
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

    def tearDown(self):
        self.selenium.quit()

    def test_Delete_Not_Existing_Experiment(self):
        exp_id = ExperimentModel.objects.all().count() + 2
        self.selenium.get(self.live_server_url + "/details/" + str(exp_id) + "/delete")
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/home")

    def test_Delete_Not_My_Experiment(self):
        exp = ExperimentModel(name="test", creator=None, latestVersion="1.0", latestStatus="paused", dataset=self.d)
        exp.save()
        self.selenium.get(self.live_server_url + "/details/" + str(exp.id) + "/delete")
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/")

    def test_Delete(self):
        self.selenium.get(self.live_server_url + "/details/" + str(self.e.pk) + "/1.0")
        self.selenium.find_element(By.ID, 'delete').click()
        self.assertEqual(ExperimentModel.objects.all().filter(pk=self.e.pk).count(), 0)
