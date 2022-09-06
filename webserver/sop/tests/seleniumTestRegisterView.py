from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTestRegisterView(LiveServerTestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.selenium = webdriver.Chrome(service=Service(ChromeDriverManager(version="105.0.5195.52").install()), options=chrome_options)
        self.selenium.implicitly_wait(10)
        self.selenium.get(self.live_server_url + "/register")

    def tearDown(self):
        self.selenium.quit()

    def test_Correct_Register(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input_one = self.selenium.find_element(By.NAME, "password1")
        password_input_one.send_keys('SOPpse22')
        password_input_two = self.selenium.find_element(By.NAME, "password2")
        password_input_two.send_keys('SOPpse22')
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys('test@gmail.com')
        self.selenium.find_element(By.CLASS_NAME, 'register_button').click()
        assert self.selenium.current_url == self.live_server_url + "/home"

    def test_Double_Register_Username(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input_one = self.selenium.find_element(By.NAME, "password1")
        password_input_one.send_keys('SOPpse22')
        password_input_two = self.selenium.find_element(By.NAME, "password2")
        password_input_two.send_keys('SOPpse22')
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys('test@gmail.com')
        self.selenium.find_element(By.CLASS_NAME, 'register_button').click()
        self.selenium.get(self.live_server_url + "/register")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input_one = self.selenium.find_element(By.NAME, "password1")
        password_input_one.send_keys('SOPpse22')
        password_input_two = self.selenium.find_element(By.NAME, "password2")
        password_input_two.send_keys('SOPpse22')
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys('test2@gmail.com')
        self.selenium.find_element(By.CLASS_NAME, 'register_button').click()
        assert self.selenium.current_url == self.live_server_url + "/register"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "This username is already taken"

    def test_Double_Register_Email(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('testa')
        password_input_one = self.selenium.find_element(By.NAME, "password1")
        password_input_one.send_keys('SOPpse22')
        password_input_two = self.selenium.find_element(By.NAME, "password2")
        password_input_two.send_keys('SOPpse22')
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys('test@gmail.com')
        self.selenium.find_element(By.CLASS_NAME, 'register_button').click()
        self.selenium.get(self.live_server_url + "/register")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('testb')
        password_input_one = self.selenium.find_element(By.NAME, "password1")
        password_input_one.send_keys('SOPpse22')
        password_input_two = self.selenium.find_element(By.NAME, "password2")
        password_input_two.send_keys('SOPpse22')
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys('test@gmail.com')
        self.selenium.find_element(By.CLASS_NAME, 'register_button').click()
        assert self.selenium.current_url == self.live_server_url + "/register"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "Email exists"

    def test_Incorrect_Register_Weak_Password(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input_one = self.selenium.find_element(By.NAME, "password1")
        password_input_one.send_keys('12345678')
        password_input_two = self.selenium.find_element(By.NAME, "password2")
        password_input_two.send_keys('12345678')
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys('test@gmail.com')
        self.selenium.find_element(By.CLASS_NAME, 'register_button').click()
        assert self.selenium.current_url == self.live_server_url + "/register"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "This password is too common."

    def test_Incorrect_Register_Short_Password(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input_one = self.selenium.find_element(By.NAME, "password1")
        password_input_one.send_keys('12')
        password_input_two = self.selenium.find_element(By.NAME, "password2")
        password_input_two.send_keys('12')
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys('test@gmail.com')
        self.selenium.find_element(By.CLASS_NAME, 'register_button').click()
        assert self.selenium.current_url == self.live_server_url + "/register"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "This password is too short. It must contain at least 8 characters."

    def test_Incorrect_Register_Invalid_Email(self):
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('test')
        password_input_one = self.selenium.find_element(By.NAME, "password1")
        password_input_one.send_keys('PSEsop22')
        password_input_two = self.selenium.find_element(By.NAME, "password2")
        password_input_two.send_keys('PSEsop22')
        email_input = self.selenium.find_element(By.NAME, "email")
        email_input.send_keys('test@gmail')
        self.selenium.find_element(By.CLASS_NAME, 'register_button').click()
        assert self.selenium.current_url == self.live_server_url + "/register"
        assert self.selenium.find_element(By.CLASS_NAME, "error_div").text == "Enter a valid email address."
