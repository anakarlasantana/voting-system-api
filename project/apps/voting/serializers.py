from rest_framework import serializers
from .models import Topic, VotingSession, Vote


class TopicSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ["id", "title", "description", "status", "created_at"]

    def get_status(self, obj):
        return obj.computed_status


class VotingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VotingSession
        fields = ["id", "topic", "start_time", "end_time"]


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id", "choice", "created_at"]
