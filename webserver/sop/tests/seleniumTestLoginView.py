from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTestLoginView(LiveServerTestCase):
    def setUp(self):
        User.objects.create_user("test", "test@gmail.com", "testpasw")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.selenium = webdriver.Chrome(service=Service(ChromeDriverManager(version="105.0.5195.52").install()), options=chrome_options)
        self.selenium.implicitly_wait(10)
        self.selenium.get(self.live_server_url + "/login")

    def tearDown(self):
        self.selenium.quit()

    def test_Correct_Login(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('testpasw')
        self.selenium.find_element(By.CLASS_NAME, 'login_button').click()
        assert self.selenium.current_url == self.live_server_url + "/home"

    def test_Incorrect_Username_Login(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('wrongname')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('testpasw')
        self.selenium.find_element(By.CLASS_NAME, 'login_button').click()
        assert self.selenium.current_url == self.live_server_url + "/login"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "Invalid username or password"

    def test_Incorrect_Password_Login(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('wrongpw')
        self.selenium.find_element(By.CLASS_NAME, 'login_button').click()
        assert self.selenium.current_url == self.live_server_url + "/login"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "Invalid username or password"
