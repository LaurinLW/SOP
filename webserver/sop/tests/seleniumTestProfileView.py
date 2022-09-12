from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
from sop.models import AlgorithmModel, DatasetModel


class SeleniumTestProfileView(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "testuser@example.com", "testpassw")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.selenium = webdriver.Chrome(service=Service(ChromeDriverManager(version="105.0.5195.52").install()), options=chrome_options)
        self.selenium.implicitly_wait(10)
        self.selenium.fullscreen_window()
        self.selenium.get(self.live_server_url + "/login")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('testuser')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('testpassw')
        self.selenium.find_element(By.CLASS_NAME, 'login_button').click()

    def tearDown(self):
        self.selenium.quit()

    # algorithm tests
    def test_Single_Algorithm_Upload(self):
        self.selenium.get(self.live_server_url + '/uploadAlgorithm')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/ecod.py"))
        self.selenium.find_element(By.ID, 'name_input').send_keys("testalgorithm")
        Select(self.selenium.find_element(By.ID, 'category')).select_by_value('Probabilistic')
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        algo = AlgorithmModel.objects.get(name="testalgorithm")
        assert algo is not None
        assert algo.creator == self.user
        assert AlgorithmModel.objects.filter(creator=self.user).count() == 1

    def test_Multiple_Algorithm_Uploads(self):
        for i in range(100):
            self.selenium.get(self.live_server_url + '/uploadAlgorithm')
            self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/ecod.py"))
            self.selenium.find_element(By.ID, 'name_input').send_keys("testalgorithm" + str(i))
            Select(self.selenium.find_element(By.ID, 'category')).select_by_value('Probabilistic')
            self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        algolist = AlgorithmModel.objects.filter(creator=self.user)
        assert algolist.count() == 100

    def test_Upload_Same_Name_Algorithm(self):
        self.selenium.get(self.live_server_url + '/uploadAlgorithm')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/ecod.py"))
        self.selenium.find_element(By.ID, 'name_input').send_keys("testalgorithm")
        Select(self.selenium.find_element(By.ID, 'category')).select_by_value('Probabilistic')
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()

        self.selenium.get(self.live_server_url + '/uploadAlgorithm')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/ecod.py"))
        self.selenium.find_element(By.ID, 'name_input').send_keys("testalgorithm")
        Select(self.selenium.find_element(By.ID, 'category')).select_by_value('Linear Model')
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        algolist = AlgorithmModel.objects.filter(creator=self.user)
        assert algolist.count() == 1
        assert self.selenium.find_element(By.CLASS_NAME, 'messages') is not None

    def test_Upload_No_Name_Algorithm(self):
        self.selenium.get(self.live_server_url + '/uploadAlgorithm')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/ecod.py"))
        Select(self.selenium.find_element(By.ID, 'category')).select_by_value('Probabilistic')
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        assert '/uploadAlgorithm' in self.selenium.current_url
        assert self.selenium.find_element(By.CLASS_NAME, 'messages') is not None

    def test_Upload_No_File_Algorithm(self):
        self.selenium.get(self.live_server_url + '/uploadAlgorithm')
        self.selenium.find_element(By.ID, 'name_input').send_keys("testalgorithm")
        Select(self.selenium.find_element(By.ID, 'category')).select_by_value('Probabilistic')
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        assert '/uploadAlgorithm' in self.selenium.current_url
        assert self.selenium.find_element(By.CLASS_NAME, 'messages') is not None

    def test_Algorithm_Pagination(self):
        for i in range(100):
            self.selenium.get(self.live_server_url + '/uploadAlgorithm')
            self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/ecod.py"))
            self.selenium.find_element(By.ID, 'name_input').send_keys("testalgorithm" + str(i))
            Select(self.selenium.find_element(By.ID, 'category')).select_by_value('Probabilistic')
            self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        algolist = AlgorithmModel.objects.filter(creator=self.user)
        assert algolist.count() == 100
        try:
            for i in range(9):
                self.selenium.find_element(By.XPATH, "//*[contains(text(), '»')]").click()
        except:
            pass
        print(self.selenium.current_url)
        assert '?algo_page=10' in self.selenium.current_url

    def test_Delete_Algorithm(self):
        self.selenium.get(self.live_server_url + '/uploadAlgorithm')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/ecod.py"))
        self.selenium.find_element(By.ID, 'name_input').send_keys("testalgorithm")
        Select(self.selenium.find_element(By.ID, 'category')).select_by_value('Probabilistic')
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        assert AlgorithmModel.objects.filter(creator=self.user).count() == 1
        self.selenium.find_element(By.ID, 'delete_algo_dataset').click()
        assert AlgorithmModel.objects.filter(creator=self.user).count() == 0

    def test_All_Categories(self):
        self.selenium.get(self.live_server_url + '/uploadAlgorithm')
        category_list_raw = Select(self.selenium.find_element(By.ID, 'category')).options
        category_list = []
        for category_raw in category_list_raw:
            category_list.append(category_raw.get_attribute('value'))
        for category in category_list:
            self.selenium.get(self.live_server_url + '/uploadAlgorithm')
            self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/ecod.py"))
            self.selenium.find_element(By.ID, 'name_input').send_keys(category)
            Select(self.selenium.find_element(By.ID, 'category')).select_by_value(category)
            self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        algos = AlgorithmModel.objects.filter(creator=self.user)
        assert algos.count() == 6
        for algo in algos:
            assert algo.name == algo.category

    # dataset tests
    def test_Single_Dataset_Upload(self):
        self.selenium.get(self.live_server_url + '/uploadDataset')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/network_intrusions_short.csv"))
        self.selenium.find_element(By.ID, 'name_input').send_keys("testdataset")
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        dataset = DatasetModel.objects.get(name="testdataset")
        assert dataset is not None
        assert dataset.creator == self.user
        assert DatasetModel.objects.filter(creator=self.user).count() == 1

    def test_Multiple_Dataset_Uploads(self):
        for i in range(100):
            self.selenium.get(self.live_server_url + '/uploadDataset')
            self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/network_intrusions_short.csv"))
            self.selenium.find_element(By.ID, 'name_input').send_keys("testdataset" + str(i))
            self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        datalist = DatasetModel.objects.filter(creator=self.user)
        assert datalist.count() == 100

    def test_Upload_Same_Name_Dataset(self):
        self.selenium.get(self.live_server_url + '/uploadDataset')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/network_intrusions_short.csv"))
        self.selenium.find_element(By.ID, 'name_input').send_keys("testdataset")
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()

        self.selenium.get(self.live_server_url + '/uploadDataset')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/network_intrusions_short.csv"))
        self.selenium.find_element(By.ID, 'name_input').send_keys("testdataset")
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        datalist = DatasetModel.objects.filter(creator=self.user)
        assert datalist.count() == 1
        assert self.selenium.find_element(By.CLASS_NAME, 'messages') is not None

    def test_Upload_No_Name_Dataset(self):
        self.selenium.get(self.live_server_url + '/uploadDataset')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/network_intrusions_short.csv"))
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        assert '/uploadDataset' in self.selenium.current_url
        assert self.selenium.find_element(By.CLASS_NAME, 'messages') is not None

    def test_Upload_No_File_Dataset(self):
        self.selenium.get(self.live_server_url + '/uploadDataset')
        self.selenium.find_element(By.ID, 'name_input').send_keys("testdataset")
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        assert '/uploadDataset' in self.selenium.current_url
        assert self.selenium.find_element(By.CLASS_NAME, 'messages') is not None

    def test_Dataset_Pagination(self):
        for i in range(100):
            self.selenium.get(self.live_server_url + '/uploadDataset')
            self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/network_intrusions_short.csv"))
            self.selenium.find_element(By.ID, 'name_input').send_keys("testdataset" + str(i))
            self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        datalist = DatasetModel.objects.filter(creator=self.user)
        assert datalist.count() == 100
        try:
            for i in range(9):
                self.selenium.find_element(By.XPATH, "//*[contains(text(), '»')]").click()
        except:
            pass
        print(self.selenium.current_url)
        assert '?data_page=10' in self.selenium.current_url

    def test_Delete_Dataset(self):
        self.selenium.get(self.live_server_url + '/uploadDataset')
        self.selenium.find_element(By.ID, 'select_file').send_keys(os.path.abspath("sop/tests/testfiles/network_intrusions_short.csv"))
        self.selenium.find_element(By.ID, 'name_input').send_keys("testdataset")
        self.selenium.find_element(By.ID, 'upload_algorithm_button').click()
        assert DatasetModel.objects.filter(creator=self.user).count() == 1
        self.selenium.find_element(By.ID, 'delete_algo_dataset').click()
        assert AlgorithmModel.objects.filter(creator=self.user).count() == 0
