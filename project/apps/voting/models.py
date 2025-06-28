from django.db import models
from django.utils import timezone
from apps.authentication.models import User


class Topic(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Aguardando Abertura"),
        ("open", "Sessão Aberta"),
        ("closed", "Votação Encerrada"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def computed_status(self):
        now = timezone.now()
        open_sessions = self.sessions.filter(
            start_time__lte=now, end_time__gt=now
        )
        if open_sessions.exists():
            return "open"
        closed_sessions = self.sessions.filter(end_time__lte=now)
        if closed_sessions.exists() and not open_sessions.exists():
            return "closed"
        return "waiting"


class VotingSession(models.Model):
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="sessions"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()

    def is_open(self):
        return self.start_time <= timezone.now() < self.end_time


class Vote(models.Model):
    VOTE_CHOICES = (
        ("Sim", "Sim"),
        ("Não", "Não"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    choice = models.CharField(max_length=3, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "topic")
