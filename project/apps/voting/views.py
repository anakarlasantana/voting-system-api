from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from .models import Topic, VotingSession, Vote
from .serializers import (
    TopicSerializer,
    VotingSessionSerializer,
    VoteSerializer,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)


@extend_schema(
    tags=["Pautas"],
    request=TopicSerializer,
    responses={200: TopicSerializer(many=True), 201: TopicSerializer},
)
class TopicView(generics.ListCreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]


@extend_schema(
    tags=["Sessões"],
    parameters=[
        OpenApiParameter(
            name="duration_minutes",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Duração da sessão em minutos (padrão 1)",
            required=False,
        ),
    ],
    responses={
        201: VotingSessionSerializer,
        400: OpenApiResponse(
            description="Já existe uma sessão aberta para essa pauta"
        ),
    },
)
class CreateSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        now = timezone.now()
        # sessions é o related_name para as sessões do tópico (plural)
        open_sessions = topic.sessions.filter(
            start_time__lte=now, end_time__gt=now
        )
        if open_sessions.exists():
            return Response(
                {"error": "Já existe uma sessão aberta para essa pauta"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            duration = int(request.query_params.get("duration_minutes", 1))
        except ValueError:
            duration = 1

        end_time = now + timedelta(minutes=duration)

        session = VotingSession.objects.create(topic=topic, end_time=end_time)
        serializer = VotingSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Votos"],
    request=VoteSerializer,
    responses={
        201: VoteSerializer,
        400: OpenApiResponse(
            description="Erro de validação ou votação duplicada"
        ),
        404: OpenApiResponse(description="Sessão não encontrada"),
    },
)
class VoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)

        now = timezone.now()
        open_sessions = topic.sessions.filter(
            start_time__lte=now, end_time__gt=now
        )
        if not open_sessions.exists():
            return Response(
                {
                    "error": "Sessão não encontrada ou não está aberta para essa pauta"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if Vote.objects.filter(user=request.user, topic=topic).exists():
            return Response(
                {"error": "Você já votou nessa pauta"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        choice = request.data.get("choice")
        if choice not in ["Sim", "Não"]:
            return Response(
                {"error": "Voto inválido. Use 'Sim' ou 'Não'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vote = Vote.objects.create(
            user=request.user, topic=topic, choice=choice
        )
        return Response(
            VoteSerializer(vote).data, status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=["Resultados"],
    responses={
        200: None,
        400: OpenApiResponse(description="Sessão ainda está aberta"),
        404: OpenApiResponse(description="Sessão não encontrada"),
    },
)
class VotingResultView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        now = timezone.now()

        # Pega a última sessão da pauta (ordenada pelo fim da sessão)
        last_session = topic.sessions.order_by("-end_time").first()

        if not last_session:
            return Response(
                {"error": "Sessão não encontrada para essa pauta"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Se a sessão ainda estiver aberta, não retorna resultado
        if last_session.start_time <= now < last_session.end_time:
            return Response(
                {"error": "Sessão ainda está aberta"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        votes = Vote.objects.filter(topic=topic)
        total = votes.count()
        sim = votes.filter(choice="Sim").count()
        nao = votes.filter(choice="Não").count()

        return Response(
            {"total": total, "sim": sim, "nao": nao},
            status=status.HTTP_200_OK,
        )
