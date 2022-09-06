from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from sop.models import ExperimentModel, VersionModel, DatasetModel


class SeleniumTestDuplicateView(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        self.d = DatasetModel(name="test", creator=self.user)
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
        self.selenium.find_element(By.ID, "duplicate").click()

    def tearDown(self):
        self.selenium.quit()

    def test_Correct_Duplicate_Name(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("duplicate_test")
        self.selenium.find_element(By.ID, "create_button").click()
        new_experiment = ExperimentModel.objects.get(name="duplicate_test")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.0")
        self.assertEqual(ExperimentModel.objects.get(name="duplicate_test").name, "duplicate_test")
        self.assertEqual(VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).filter(runs=0).count(), 1)
        duplicate_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        duplicate_one = VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).filter(runs=0)[0]
        self.assertEqual(duplicate_zero.seed, duplicate_one.seed)
        self.assertEqual(duplicate_zero.numberSubspaces, duplicate_one.numberSubspaces)
        self.assertEqual(duplicate_zero.minDimension, duplicate_one.minDimension)
        self.assertEqual(duplicate_zero.maxDimension, duplicate_one.maxDimension)
        self.assertEqual(duplicate_zero.algorithms.count(), duplicate_one.algorithms.count())

    def test_Correct_Duplicate_Repetitions(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("duplicate_test_repetitions")
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.clear()
        repetitions_input.send_keys("2")
        self.selenium.find_element(By.ID, "create_button").click()
        new_experiment = ExperimentModel.objects.get(name="duplicate_test_repetitions")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.0")
        self.assertEqual(ExperimentModel.objects.get(name="duplicate_test_repetitions").name, "duplicate_test_repetitions")
        self.assertEqual(VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).count(), 2)
        duplicate_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        duplicate_one = VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).filter(runs=0)[0]
        self.assertEqual(duplicate_zero.seed, duplicate_one.seed)
        self.assertEqual(duplicate_zero.numberSubspaces, duplicate_one.numberSubspaces)
        self.assertEqual(duplicate_zero.minDimension, duplicate_one.minDimension)
        self.assertEqual(duplicate_zero.maxDimension, duplicate_one.maxDimension)
        self.assertEqual(duplicate_zero.algorithms.count(), duplicate_one.algorithms.count())

    def test_Correct_Duplicate_NumberSubspaces(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("duplicate_test_numberSubspaces")
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.clear()
        numberSubspaces_input.send_keys("2")
        self.selenium.find_element(By.ID, "create_button").click()
        new_experiment = ExperimentModel.objects.get(name="duplicate_test_numberSubspaces")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.0")
        self.assertEqual(ExperimentModel.objects.get(name="duplicate_test_numberSubspaces").name, "duplicate_test_numberSubspaces")
        self.assertEqual(VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).count(), 1)
        duplicate_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        duplicate_one = VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).filter(runs=0)[0]
        self.assertEqual(duplicate_zero.seed, duplicate_one.seed)
        self.assertEqual(2, duplicate_one.numberSubspaces)
        self.assertEqual(duplicate_zero.minDimension, duplicate_one.minDimension)
        self.assertEqual(duplicate_zero.maxDimension, duplicate_one.maxDimension)
        self.assertEqual(duplicate_zero.algorithms.count(), duplicate_one.algorithms.count())

    def test_Correct_Duplicate_MinDimension_MaxDimension(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("duplicate_test_dimension")
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.clear()
        minDimension_input.send_keys("2")
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.clear()
        maxDimension_input.send_keys("3")
        self.selenium.find_element(By.ID, "create_button").click()
        new_experiment = ExperimentModel.objects.get(name="duplicate_test_dimension")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.0")
        self.assertEqual(ExperimentModel.objects.get(name="duplicate_test_dimension").name, "duplicate_test_dimension")
        self.assertEqual(VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).count(), 1)
        duplicate_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        duplicate_one = VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).filter(runs=0)[0]
        self.assertEqual(duplicate_zero.seed, duplicate_one.seed)
        self.assertEqual(duplicate_zero.numberSubspaces, duplicate_one.numberSubspaces)
        self.assertEqual(2, duplicate_one.minDimension)
        self.assertEqual(3, duplicate_one.maxDimension)
        self.assertEqual(duplicate_zero.algorithms.count(), duplicate_one.algorithms.count())

    def test_Correct_Duplicate_Seed(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("duplicate_test_seed")
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.clear()
        seed_input.send_keys("2")
        self.selenium.find_element(By.ID, "create_button").click()
        new_experiment = ExperimentModel.objects.get(name="duplicate_test_seed")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.0")
        self.assertEqual(ExperimentModel.objects.get(name="duplicate_test_seed").name, "duplicate_test_seed")
        self.assertEqual(VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).count(), 1)
        duplicate_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        duplicate_one = VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).filter(runs=0)[0]
        self.assertEqual(2, duplicate_one.seed)
        self.assertEqual(duplicate_zero.numberSubspaces, duplicate_one.numberSubspaces)
        self.assertEqual(duplicate_zero.minDimension, duplicate_one.minDimension)
        self.assertEqual(duplicate_zero.maxDimension, duplicate_one.maxDimension)
        self.assertEqual(duplicate_zero.algorithms.count(), duplicate_one.algorithms.count())

    def test_Correct_Duplicate_Algorithms(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys("duplicate_test_algo")
        for collap in self.selenium.find_elements(By.CLASS_NAME, "collapsible"):
            if collap.text == "Probabilistic":
                collap.click()
        for algo in self.selenium.find_elements(By.ID, "algorithms"):
            if algo.is_displayed():
                algo.click()
        self.selenium.find_element(By.ID, "create_button").click()
        new_experiment = ExperimentModel.objects.get(name="duplicate_test_algo")
        self.assertEqual(ExperimentModel.objects.get(pk=self.e.pk).latestVersion, "1.0")
        self.assertEqual(ExperimentModel.objects.get(name="duplicate_test_algo").name, "duplicate_test_algo")
        self.assertEqual(VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).count(), 1)
        duplicate_zero = VersionModel.objects.all().filter(experiment=self.e).filter(edits=1).filter(runs=0)[0]
        duplicate_one = VersionModel.objects.all().filter(experiment=new_experiment).filter(edits=1).filter(runs=0)[0]
        self.assertEqual(duplicate_zero.seed, duplicate_one.seed)
        self.assertEqual(duplicate_zero.numberSubspaces, duplicate_one.numberSubspaces)
        self.assertEqual(duplicate_zero.minDimension, duplicate_one.minDimension)
        self.assertEqual(duplicate_zero.maxDimension, duplicate_one.maxDimension)
        self.assertNotEqual(duplicate_zero.algorithms.count(), duplicate_one.algorithms.count())

    def test_Incorrect_Duplicate_Name(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.clear()
        self.selenium.find_element(By.ID, "create_button").click()
        assert self.selenium.current_url == self.live_server_url + "/duplicate/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "The name field needs to be filled in"

    def test_Incorrect_Duplicate_NumberSubspaces(self):
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.clear()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/duplicate/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the numberSubspaces"

    def test_Incorrect_Duplicate_MinDimension(self):
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.clear()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/duplicate/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the minDimension"

    def test_Incorrect_Duplicate_MaxDimension(self):
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.clear()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/duplicate/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the maxDimension"

    def test_Incorrect_Duplicate_Seed(self):
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.clear()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/duplicate/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the seed"

    def test_Incorrect_Duplicate(self):
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
        assert self.selenium.current_url == self.live_server_url + "/duplicate/" + str(self.e.id) + "/1.0"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text != ""
