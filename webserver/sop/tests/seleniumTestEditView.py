from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from sop.models import ExperimentModel, VersionModel, DatasetModel


class SeleniumTestEditView(LiveServerTestCase):
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
        self.selenium.find_element(By.ID, "edit").click()

    def tearDown(self):
        self.selenium.quit()

    def test_Correct_Edit_Name(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("edit_test")
        self.selenium.find_element(By.ID, "create_button").click()
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "2.0")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).name, "edit_test")
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0).count(), 1)
        edit_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        edit_one = VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0)[0]
        self.assertEqual(edit_zero.seed, edit_one.seed)
        self.assertEqual(edit_zero.numberSubspaces, edit_one.numberSubspaces)
        self.assertEqual(edit_zero.minDimension, edit_one.minDimension)
        self.assertEqual(edit_zero.maxDimension, edit_one.maxDimension)
        self.assertEqual(edit_zero.algorithms.count(), edit_one.algorithms.count())
        self.assertEqual(edit_zero.experiment, edit_one.experiment)

    def test_Correct_Edit_Seed(self):
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.clear()
        seed_input.send_keys("2")
        self.selenium.find_element(By.ID, "create_button").click()
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "2.0")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).name, "test")
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0).count(), 1)
        edit_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        edit_one = VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0)[0]
        self.assertEqual(2, edit_one.seed)
        self.assertEqual(edit_zero.numberSubspaces, edit_one.numberSubspaces)
        self.assertEqual(edit_zero.minDimension, edit_one.minDimension)
        self.assertEqual(edit_zero.maxDimension, edit_one.maxDimension)
        self.assertEqual(edit_zero.algorithms.count(), edit_one.algorithms.count())
        self.assertEqual(edit_zero.experiment, edit_one.experiment)

    def test_Correct_Edit_numberSubspaces(self):
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.clear()
        numberSubspaces_input.send_keys("2")
        self.selenium.find_element(By.ID, "create_button").click()
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "2.0")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).name, "test")
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0).count(), 1)
        edit_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        edit_one = VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0)[0]
        self.assertEqual(edit_zero.seed, edit_one.seed)
        self.assertEqual(2, edit_one.numberSubspaces)
        self.assertEqual(edit_zero.minDimension, edit_one.minDimension)
        self.assertEqual(edit_zero.maxDimension, edit_one.maxDimension)
        self.assertEqual(edit_zero.algorithms.count(), edit_one.algorithms.count())
        self.assertEqual(edit_zero.experiment, edit_one.experiment)

    def test_Correct_Edit_minDimension_maxDimension(self):
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.clear()
        minDimension_input.send_keys("2")
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.clear()
        maxDimension_input.send_keys("3")
        self.selenium.find_element(By.ID, "create_button").click()
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "2.0")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).name, "test")
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0).count(), 1)
        edit_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        edit_one = VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0)[0]
        self.assertEqual(edit_zero.seed, edit_one.seed)
        self.assertEqual(edit_zero.numberSubspaces, edit_one.numberSubspaces)
        self.assertEqual(2, edit_one.minDimension)
        self.assertEqual(3, edit_one.maxDimension)
        self.assertEqual(edit_zero.algorithms.count(), edit_one.algorithms.count())
        self.assertEqual(edit_zero.experiment, edit_one.experiment)

    def test_Correct_Edit_Algorithms(self):
        for collap in self.selenium.find_elements(By.CLASS_NAME, "collapsible"):
            if collap.text == "Probabilistic":
                collap.click()
        for algo in self.selenium.find_elements(By.ID, "algorithms"):
            if algo.is_displayed():
                algo.click()
        self.selenium.find_element(By.ID, "create_button").click()
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "2.0")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).name, "test")
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0).count(), 1)
        edit_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        edit_one = VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0)[0]
        self.assertEqual(edit_zero.seed, edit_one.seed)
        self.assertEqual(edit_zero.numberSubspaces, edit_one.numberSubspaces)
        self.assertEqual(edit_zero.minDimension, edit_one.minDimension)
        self.assertEqual(edit_zero.maxDimension, edit_one.maxDimension)
        self.assertNotEqual(edit_zero.algorithms.count(), edit_one.algorithms.count())
        self.assertEqual(edit_zero.experiment, edit_one.experiment)

    def test_Correct_Edit_Everything(self):
        for collap in self.selenium.find_elements(By.CLASS_NAME, "collapsible"):
            if collap.text == "Probabilistic":
                collap.click()
        for algo in self.selenium.find_elements(By.ID, "algorithms"):
            if algo.is_displayed():
                algo.click()
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.clear()
        minDimension_input.send_keys("2")
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.clear()
        maxDimension_input.send_keys("3")
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.clear()
        numberSubspaces_input.send_keys("2")
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.clear()
        seed_input.send_keys("2")
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("edit_test")
        self.selenium.find_element(By.ID, "create_button").click()
        self.assertEqual(VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0).count(), 1)
        edit_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        edit_one = VersionModel.objects.all().filter(experiment=self.e).filter(edits=2).filter(runs=0)[0]
        self.assertNotEqual(edit_zero.algorithms.count(), edit_one.algorithms.count())
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "2.0")
        self.assertEqual(2, edit_one.minDimension)
        self.assertEqual(3, edit_one.maxDimension)
        self.assertEqual(2, edit_one.numberSubspaces)
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).name, "edit_test")
        self.assertEqual(2, edit_one.seed)

    def test_Incorrect_Edit_Name(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        self.selenium.find_element(By.ID, "create_button").click()
        assert self.selenium.current_url == self.live_server_url + "/edit/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "The name field needs to be filled in"

    def test_Incorrect_Edit_NumberSubspaces(self):
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.clear()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/edit/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the numberSubspaces"

    def test_Incorrect_Edit_MinDimension(self):
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.clear()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/edit/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the minDimension"

    def test_Incorrect_Edit_MaxDimension(self):
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.clear()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/edit/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the maxDimension"

    def test_Incorrect_Edit_Seed(self):
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.clear()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/edit/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the seed"

    def test_Incorrect_Edit(self):
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.clear()
        minDimension_input.send_keys("a")
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.clear()
        maxDimension_input.send_keys("b")
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.clear()
        numberSubspaces_input.send_keys("c")
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.clear()
        seed_input.send_keys("d")
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        self.selenium.find_element(By.ID, "create_button").click()
        assert self.selenium.current_url == self.live_server_url + "/edit/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text != ""
