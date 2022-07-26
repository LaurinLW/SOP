from django.test import TestCase, Client
from django.http import HttpResponseRedirect, HttpResponse


class TestRegiserView(TestCase):
    def setUp(self):
        pass

    def testRegister(self):
        c = Client()
        response = c.post("/register", {'username': 'test', 'password1': 'SOPpse22', 'password2': 'SOPpse22', 'email': 'test@gmail.com'})
        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertTrue(response.has_header("Location"))
        self.assertEqual(response.headers.get("Location"), "/home")

    def testDoubleRegister(self):
        c = Client()
        response1 = c.post("/register", {'username': 'test', 'password1': 'SOPpse22', 'password2': 'SOPpse22', 'email': 'test@gmail.com'})
        response2 = c.post("/register", {'username': 'test', 'password1': 'SOPpse22', 'password2': 'SOPpse22', 'email': 'test@gmail.com'})
        self.assertNotEqual(type(response1), type(response2))

    def testWrongPassword(self):
        c = Client()
        response = c.post("/register", {'username': 'test', 'password1': '12345678', 'password2': '12345678', 'email': 'test@gmail.com'})
        self.assertEqual(type(response), HttpResponse)
        self.assertFalse(response.has_header("Location"))

    def testPasswordsDontMatch(self):
        c = Client()
        response = c.post("/register", {'username': 'test', 'password1': 'SOPpse22', 'password2': 'PSEsop22', 'email': 'test@gmail.com'})
        self.assertEqual(type(response), HttpResponse)
        self.assertFalse(response.has_header("Location"))
