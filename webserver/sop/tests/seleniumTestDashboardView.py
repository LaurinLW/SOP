from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from django.core.files.base import File
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from sop.models import ExperimentModel, VersionModel, DatasetModel
from sop.metrics.views import TableView
import numpy as np
import pandas as pd


class SeleniumTestDashboardView(LiveServerTestCase):
    def setUp(self):
        TableView.PAGE_SIZE = 50

        self.user = User.objects.create_user("test", "test@gmail.com", "testpasw")

        df = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list('ABCD'))
        df.to_csv('dataset.csv')

        self.d = DatasetModel()
        self.d.file.save('dataset.csv', File(open('dataset.csv')))
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

    def tearDown(self):
        self.selenium.quit()

    def test_No_Metric(self):
        self.selenium.get(self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0")
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric")

    def test_Unknown_Metric(self):
        self.selenium.get(self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/UnknownMetric")
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric")

    def test_Page_out_of_Range(self):
        self.selenium.get(self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric?page=4")
        page_counter = self.selenium.find_element(By.ID, 'page')
        self.assertEqual(page_counter.get_property('value'), "0")

    def test_Page_Backwards(self):
        self.selenium.get(self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric?page=1")
        self.selenium.find_element(By.ID, "prev_page").click()
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric?page=0")

    def test_Page_Forwards(self):
        self.selenium.get(self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric")
        self.selenium.find_element(By.ID, "next_page").click()
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric?page=1")

    def test_Page_Backwards_Not_Possible(self):
        self.selenium.get(self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric")
        self.assertRaises(NoSuchElementException, self.selenium.find_element, By.ID, "prev_page")

    def test_Page_Forwards_Not_Possible(self):
        self.selenium.get(self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric?page=1")
        self.assertRaises(NoSuchElementException, self.selenium.find_element, By.ID, "next_page")

    def test_Filter(self):
        self.selenium.get(self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric?page=1")
        filter_input = self.selenium.find_element(By.ID, "filter")
        filter_input.send_keys('select=A')
        self.selenium.find_element(By.ID, "filter_button").click()
        self.assertEqual(self.selenium.current_url, self.live_server_url + "/dashboard/" + str(self.e.pk) + "/1.0/TestMetric?filter=select%3DA&page=1")
