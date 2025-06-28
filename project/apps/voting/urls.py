from django.urls import path
from .views import (
    TopicView,
    CreateSessionView,
    VoteView,
    VotingResultView,
)

urlpatterns = [
    path("topics/", TopicView.as_view(), name="topics"),
    path(
        "topics/<int:topic_id>/session/",
        CreateSessionView.as_view(),
        name="session-create",
    ),
    path("topics/<int:topic_id>/vote/", VoteView.as_view(), name="vote"),
    path(
        "topics/<int:topic_id>/result/",
        VotingResultView.as_view(),
        name="result",
    ),
]
