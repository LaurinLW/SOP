from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect


class TestLoginView(TestCase):
    def setUp(self):
        User.objects.create_user("test", "test@gmail.com", "testpasw")

    def testLogin(self):
        c = Client()
        response = c.post("/login", {'username': 'test', 'password': 'testpasw'})
        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertTrue(response.has_header("Location"))
        self.assertEqual(response.headers.get("Location"), "/home")

    def testWrongPasswordLogin(self):
        c = Client()
        response = c.post("/login", {'username': 'test', 'password': 'wrongpw'})
        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertTrue(response.has_header("Location"))
        self.assertEqual(response.headers.get("Location"), "/login")

    def testWrongUsernameLogin(self):
        c = Client()
        response = c.post("/login", {'username': 'wrongname', 'password': 'testpasw'})
        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertTrue(response.has_header("Location"))
        self.assertEqual(response.headers.get("Location"), "/login")
