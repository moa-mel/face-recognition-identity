from django.shortcuts import render

from user.serializer import RegisterSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status

# Create your views here.
class RegisterUserView(GenericAPIView):
    serializer_class = RegisterSerializer
    throttle_scope = "anon"
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                "message": "User registered successfully.",
            },
            status=status.HTTP_201_CREATED
        )

       