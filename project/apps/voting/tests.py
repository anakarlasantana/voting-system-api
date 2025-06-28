from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.authentication.models import User
from .models import Topic, VotingSession, Vote


class VotingTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            cpf="12345678901", name="Test User", password="senha123"
        )

        # Autenticar via JWT
        login_url = reverse("login")  # Certifique-se que existe esta rota
        response = self.client.post(
            login_url, {"cpf": "12345678901", "password": "senha123"}
        )
        self.assertEqual(response.status_code, 200)
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.topic = Topic.objects.create(
            title="Teste Pauta", description="Descrição"
        )

    def test_create_voting_session_default_duration(self):
        url = reverse("session-create", args=[self.topic.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        session = VotingSession.objects.get(topic=self.topic)
        self.assertIsNotNone(session)
        self.assertTrue(session.end_time > timezone.now())

    def test_create_voting_session_with_custom_duration(self):
        url = (
            reverse("session-create", args=[self.topic.id])
            + "?duration_minutes=5"
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        session = VotingSession.objects.get(topic=self.topic)
        expected_end = session.start_time + timedelta(minutes=5)
        self.assertAlmostEqual(
            session.end_time.timestamp(), expected_end.timestamp(), delta=5
        )

    def test_create_session_already_exists(self):
        VotingSession.objects.create(
            topic=self.topic, end_time=timezone.now() + timedelta(minutes=1)
        )
        url = reverse("session-create", args=[self.topic.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_vote_success(self):
        VotingSession.objects.create(
            topic=self.topic, end_time=timezone.now() + timedelta(minutes=5)
        )
        url = reverse("vote", args=[self.topic.id])
        response = self.client.post(url, {"choice": "Sim"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Vote.objects.filter(user=self.user, topic=self.topic).count(), 1
        )

    def test_vote_twice_for_same_topic(self):
        VotingSession.objects.create(
            topic=self.topic, end_time=timezone.now() + timedelta(minutes=5)
        )
        Vote.objects.create(user=self.user, topic=self.topic, choice="Sim")
        url = reverse("vote", args=[self.topic.id])
        response = self.client.post(url, {"choice": "Não"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_vote_invalid_choice(self):
        VotingSession.objects.create(
            topic=self.topic, end_time=timezone.now() + timedelta(minutes=5)
        )
        url = reverse("vote", args=[self.topic.id])
        response = self.client.post(url, {"choice": "Talvez"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_vote_no_session(self):
        url = reverse("vote", args=[self.topic.id])
        response = self.client.post(url, {"choice": "Sim"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)

    def test_vote_session_closed(self):
        VotingSession.objects.create(
            topic=self.topic, end_time=timezone.now() - timedelta(minutes=1)
        )
        url = reverse("vote", args=[self.topic.id])
        response = self.client.post(url, {"choice": "Sim"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_get_results_session_closed(self):
        VotingSession.objects.create(
            topic=self.topic, end_time=timezone.now() - timedelta(minutes=1)
        )
        Vote.objects.create(user=self.user, topic=self.topic, choice="Sim")
        url = reverse("result", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["sim"], 1)
        self.assertEqual(response.data["nao"], 0)

    def test_get_results_session_open(self):
        VotingSession.objects.create(
            topic=self.topic, end_time=timezone.now() + timedelta(minutes=5)
        )
        url = reverse("result", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_get_results_no_session(self):
        url = reverse("result", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
