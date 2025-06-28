from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer


class RegisterView(APIView):

    @extend_schema(
        tags=["Autenticação"],
        request=RegisterSerializer,
        responses={201: None, 400: RegisterSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Usuário registrado com sucesso!"},
            status=status.HTTP_201_CREATED,
        )
