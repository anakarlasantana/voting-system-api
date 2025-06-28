from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from apps.authentication.models import User


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.me_url = reverse("me")
        self.user_data = {
            "cpf": "12345678901",
            "name": "Usuário Teste",
            "password": "senha123",
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(cpf=self.user_data["cpf"]).exists()
        )

    def test_register_invalid_password(self):
        data = self.user_data.copy()
        data["password"] = "123"
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)

    def test_login_user(self):
        User.objects.create_user(
            cpf=self.user_data["cpf"],
            name=self.user_data["name"],
            password=self.user_data["password"],
        )
        response = self.client.post(
            self.login_url,
            {
                "cpf": self.user_data["cpf"],
                "password": self.user_data["password"],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url, {"cpf": "00000000000", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 401)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 401)

    def test_me_authenticated(self):
        User.objects.create_user(**self.user_data)
        login_response = self.client.post(
            self.login_url,
            {
                "cpf": self.user_data["cpf"],
                "password": self.user_data["password"],
            },
        )
        token = login_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["cpf"], self.user_data["cpf"])
        self.assertEqual(response.data["name"], self.user_data["name"])
        self.assertNotIn("password", response.data)
