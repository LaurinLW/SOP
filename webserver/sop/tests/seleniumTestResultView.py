from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from sop.models import ExperimentModel, VersionModel, DatasetModel, ResultModel
from django.core.files.base import File
import os
import time
import pandas
from zipfile import ZipFile
import io


class SeleniumTestResultView(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")
        self.d = DatasetModel()
        self.d.save()
        self.e = ExperimentModel(name="test", creator=self.user, latestVersion="1.0", latestStatus="paused", dataset=self.d)
        self.e.save()
        self.v = VersionModel(edits=1, runs=0, seed=1, status="paused", numberSubspaces=1,
                              minDimension=1, maxDimension=1, progress=0, experiment=self.e, pid=None)
        self.v.save()
        self.r = ResultModel(version=self.v)
        self.r.resultFile.save("test_save_file_1.csv", File(open(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/subspace_result0_test.csv")))
        self.r.save()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        prefs = {"download.default_directory": f'{os.path.abspath(os.getcwd())}{os.sep}sop{os.sep}tests{os.sep}testfiles'}
        chrome_options.add_experimental_option("prefs", prefs)
        self.selenium = webdriver.Chrome(service=Service(ChromeDriverManager(version="105.0.5195.52").install()), options=chrome_options)
        self.selenium.implicitly_wait(10)
        self.selenium.get(self.live_server_url + "/login")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('testpasw')
        self.selenium.find_element(By.CLASS_NAME, 'login_button').click()

    def tearDown(self):
        self.r.delete()
        if os.path.exists(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/test_save_file_1.csv"):
            os.remove(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/test_save_file_1.csv")
        if os.path.exists(os.path.abspath(os.getcwd()) + "/sop/results/test_save_file_1.csv"):
            os.remove(os.path.abspath(os.getcwd()) + "/sop/results/test_save_file_1.csv")
        if os.path.exists(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/test.1.0.zip"):
            os.remove(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/test.1.0.zip")
        if os.path.exists(os.path.abspath(os.getcwd()) + "/sop/results/test_save_file_2.csv"):
            os.remove(os.path.abspath(os.getcwd()) + "/sop/results/test_save_file_2.csv")
        self.selenium.quit()

    def test_Download_File(self):
        self.selenium.get(f'{self.live_server_url}/details/{self.e.pk}/1.0/results')
        self.selenium.find_element(By.ID, "single_download").click()
        time.sleep(1)
        assert os.path.exists(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/test_save_file_1.csv")
        same = True
        for a in pandas.read_csv(self.r.resultFile.path):
            if a not in pandas.read_csv(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/test_save_file_1.csv"):
                same = False
        assert same

    def test_Download_Zip(self):
        r2 = ResultModel(version=self.v)
        r2.resultFile.save("test_save_file_2.csv", File(open(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/subspace_result0_test.csv")))
        r2.save()
        self.selenium.get(f'{self.live_server_url}/details/{self.e.pk}/1.0/results')
        self.selenium.find_element(By.ID, "multi_download").click()
        time.sleep(1)
        assert os.path.exists(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/test.1.0.zip")
        zip_file = ZipFile(os.path.abspath(os.getcwd()) + "/sop/tests/testfiles/test.1.0.zip", "r")
        same = True
        for a in pandas.read_csv(self.r.resultFile.path):
            if a not in pandas.read_csv(io.BytesIO(zip_file.read("test_save_file_1.csv"))):
                same = False
            if a not in pandas.read_csv(io.BytesIO(zip_file.read("test_save_file_2.csv"))):
                same = False
        assert same
        r2.delete()
