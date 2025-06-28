from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, UserSerializer


@extend_schema(
    tags=["Autenticação"],
    request=RegisterSerializer,
    responses={201: None, 400: RegisterSerializer},
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=["Autenticação"],
    request=TokenObtainPairView.serializer_class,
    responses={200: TokenObtainPairView.serializer_class},
)
class LoginView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(
    tags=["Autenticação"],
    responses={200: UserSerializer},
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
