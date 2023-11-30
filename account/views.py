import datetime

import jwt
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django_countries import countries
from django_filters.rest_framework import DjangoFilterBackend
from django_rest_passwordreset.views import ResetPasswordRequestToken
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User
from account.pagination import CustomPageNumberPagination
from account.serializers import (ChangePasswordSerializer, RegisterSerializer,
                                 UserSerializer)


class RegisterAPIView(GenericAPIView):
    """
    API endpoint that allows users to be created.

    Expected payload:
    {
      "password": "password",
      "first_name": "John",
      "last_name": "Doe",
      "email": "johndoe@example.com",
      "accepts_newsletters": true,
      "accepts_terms_and_conditions": true,
      "profile": {
        "country": "US"
      }
    }
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.email_verified = False  # Set email_verified to False initially
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Authentication Expired")
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            # Set the token expiration to a past date to invalidate it
            token.set_exp(lifetime=timezone.timedelta(seconds=0))
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    

# class LogoutAPIView(APIView):
#     def post(self, request):
#         response = Response()
#         response.delete_cookie("jwt")
#         response.data = {
#             'message': "success"
#         }
#         return response


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed, edited and searched.
    """
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    lookup_field = 'id'
    filterset_fields = ['id', 'username', 'email']  
    search_fields = ['id', 'username', 'email']  
    ordering_fields = ['id', 'username', 'email']  


class CurrentUserDetailView(APIView):
    """
    An endpoint to get the current logged in users' details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user 
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
