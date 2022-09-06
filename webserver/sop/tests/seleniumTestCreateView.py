from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from sop.models import DatasetModel, AlgorithmModel


class SeleniumTestCreateView(LiveServerTestCase):
    def setUp(self):
        user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        d = DatasetModel(name="test", creator=user)
        d.save()
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
        self.selenium.find_element(By.ID, 'new_experiment').click()

    def tearDown(self):
        self.selenium.quit()

    def test_Correct_Create_No_Algorithm(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('1')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url.__contains__("/details/")

    def test_Correct_Create_Few_Algorithm(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('1')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        for collap in self.selenium.find_elements(By.CLASS_NAME, "collapsible"):
            if collap.text == "Probabilistic" or collap.text == "Proximity-Based":
                collap.click()
        for algo in self.selenium.find_elements(By.ID, "algorithms"):
            if algo.is_displayed():
                algo.click()
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url.__contains__("/details/")

    def test_Incorrect_Create_Name(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('1')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "The name field needs to be filled in"

    def test_Incorrect_Create_Repetitions(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('1')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the repetitions"

    def test_Incorrect_Create_NumberSubspaces(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('1')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the numberSubspaces"

    def test_Incorrect_Create_minDimension(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the minDimension"

    def test_Incorrect_Create_maxDimension(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('1')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the maxDimension"

    def test_Incorrect_Create_Seed(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('1')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "You need to specify the seed"

    def test_Incorrect_Create(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('a')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('b')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('c')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('d')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('e')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text != ""

    def test_Incorrect_Create_MinDimension_MaxDimension(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('2')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "Your min dimension can not be bigger than the max dimension"

    def test_Incorrect_Algorithm_Parameter(self):
        name_input = self.selenium.find_element(By.ID, "name")
        name_input.send_keys('test')
        repetitions_input = self.selenium.find_element(By.ID, "repetitions")
        repetitions_input.send_keys('1')
        numberSubspaces_input = self.selenium.find_element(By.ID, "numberSubspaces")
        numberSubspaces_input.send_keys('1')
        minDimension_input = self.selenium.find_element(By.ID, "minDimension")
        minDimension_input.send_keys('1')
        maxDimension_input = self.selenium.find_element(By.ID, "maxDimension")
        maxDimension_input.send_keys('1')
        seed_input = self.selenium.find_element(By.ID, "seed")
        seed_input.send_keys('1')
        for collap in self.selenium.find_elements(By.CLASS_NAME, "collapsible"):
            if collap.text == "Probabilistic":
                collap.click()
        for algo in self.selenium.find_elements(By.ID, "algorithms"):
            if int(algo.get_attribute("value")) == AlgorithmModel.objects.get(name="abod").pk:
                algo.click()
        param = self.selenium.find_element(By.ID, f'{AlgorithmModel.objects.get(name="abod").pk}.parameters:contamination')
        param.send_keys("value", "a")
        self.selenium.find_element(By.ID, 'create_button').click()
        assert self.selenium.current_url == self.live_server_url + "/newExperiment"
