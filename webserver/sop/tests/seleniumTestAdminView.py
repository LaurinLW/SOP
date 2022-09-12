from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTestAdminView(LiveServerTestCase):

    def setUp(self):
        self.user = User.objects.create_user("testadmin", "testadmin@example.com", "testpassw")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.selenium = webdriver.Chrome(service=Service(ChromeDriverManager(version="105.0.5195.52").install()), options=chrome_options)
        self.selenium.implicitly_wait(10)
        self.selenium.fullscreen_window()
        self.selenium.get(self.live_server_url + "/login")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('testadmin')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('testpassw')
        self.selenium.find_element(By.CLASS_NAME, 'login_button').click()

    def tearDown(self):
        self.selenium.quit()

    # user tests
    def test_Multiple_Users(self):
        self.selenium.get(self.live_server_url + '/profile')
        for i in range(100):
            User.objects.create_user("testuser" + str(i), "testuser@example.com", "testpassw").save()
        userlist = User.objects.all()
        assert userlist.count() == 101

    def test_Create_Same_Name_User(self):
        self.selenium.get(self.live_server_url + '/uploadAlgorithm')
        User.objects.create_user("testuser", "testuser@example.com", "testpassw").save()
        try:
            User.objects.create_user("testuser", "testuser@example.com", "testpassw").save()
        except:
            pass
        userlist = User.objects.all()
        assert userlist.count() == 2

    def test_User_Pagination(self):
        self.selenium.get(self.live_server_url + '/profile')
        for i in range(14):
            User.objects.create_user("testuser" + str(i), "testuser" + str(i) + "@example.com", "testpassw").save()
        userlist = User.objects.all()
        assert userlist.count() == 15
        try:
            self.selenium.get(self.live_server_url + '/profile?user_page=1')
            self.selenium.get(self.live_server_url + '/profile?user_page=2')
            self.selenium.get(self.live_server_url + '/profile?user_page=3')
        except:
            pass
        assert '?user_page=3' in self.selenium.current_url
