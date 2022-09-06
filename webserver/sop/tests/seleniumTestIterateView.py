from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from sop.models import ExperimentModel, VersionModel, DatasetModel


class SeleniumTestIterateView(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        self.d = DatasetModel()
        self.d.save()
        self.e = ExperimentModel(name="test", creator=self.user, latestVersion="1.0", latestStatus="paused", dataset=self.d)
        self.e.save()
        self.v = VersionModel(edits=1, runs=0, seed=1, status="running", numberSubspaces=1, minDimension=1, maxDimension=1, progress=0, experiment=self.e)
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

    def testIterateOneTime(self):
        self.selenium.find_element(By.ID, "iterate").click()
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/details/" + str(self.e.pk) + "/1.1")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.1")
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=1).count(), 1)
        iteration_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        iteration_one = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=1)[0]
        self.assertEqual(iteration_zero.seed, iteration_one.seed - 1)
        self.assertEqual(iteration_zero.numberSubspaces, iteration_one.numberSubspaces)
        self.assertEqual(iteration_zero.minDimension, iteration_one.minDimension)
        self.assertEqual(iteration_zero.maxDimension, iteration_one.maxDimension)
        self.assertEqual(iteration_zero.algorithms.count(), iteration_one.algorithms.count())
        self.assertEqual(iteration_zero.experiment, iteration_one.experiment)

    def testIterateManyTimes(self):
        for i in range(100):
            self.selenium.find_element(By.ID, "iterate").click()
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/details/" + str(self.e.pk) + "/1.100")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.100")
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=1).count(), 1)
        iteration_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        iteration_final = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=100)[0]
        self.assertEqual(iteration_zero.seed + 100, iteration_final.seed)
        self.assertEqual(iteration_zero.numberSubspaces, iteration_final.numberSubspaces)
        self.assertEqual(iteration_zero.minDimension, iteration_final.minDimension)
        self.assertEqual(iteration_zero.maxDimension, iteration_final.maxDimension)
        self.assertEqual(iteration_zero.algorithms.count(), iteration_final.algorithms.count())
        self.assertEqual(iteration_zero.experiment, iteration_final.experiment)

    def testIterateSomeVersion(self):
        for i in range(99):
            self.selenium.find_element(By.ID, "iterate").click()
        self.selenium.get(self.live_server_url + "/details/" + str(self.e.pk) + "/1.50")
        self.selenium.find_element(By.ID, "iterate").click()
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/details/" + str(self.e.pk) + "/1.100")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.100")
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=1).count(), 1)
        iteration_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        iteration_final = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=100)[0]
        self.assertEqual(iteration_zero.seed + 100, iteration_final.seed)
        self.assertEqual(iteration_zero.numberSubspaces, iteration_final.numberSubspaces)
        self.assertEqual(iteration_zero.minDimension, iteration_final.minDimension)
        self.assertEqual(iteration_zero.maxDimension, iteration_final.maxDimension)
        self.assertEqual(iteration_zero.algorithms.count(), iteration_final.algorithms.count())
        self.assertEqual(iteration_zero.experiment, iteration_final.experiment)
