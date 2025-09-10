from rest_framework import generics
from rest_framework.permissions import IsAuthenticated , AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .authentication import CookieJWTAuthentication

class RefreshTokenView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"error": "No refresh token"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)

            response = Response({"message": "Token refreshed"})
            response.set_cookie(
                key="access_token",
                value=new_access,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Strict",
                max_age=60 * 10,  # 10 mins
            )
            return response
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=400)


User = get_user_model()


#  Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    authentication_classes = []


#  Login
# class LoginView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data  # contains access + refresh

        access_token = tokens["access"]
        refresh_token = tokens["refresh"]

        # Set cookies
        response = Response(
            {"message": "Login successful"},
            status=status.HTTP_200_OK
        )
        # Access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,  # Secure only in production
            samesite="Strict",
            max_age=60 * 10,  # 10 mins
        )
        # Refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Strict",
            max_age=60 * 60 * 24 * 7,  # 7 days
        )

        return response
#Delete the access and refresh tokens from the cookies
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    def post(self,request,*args,**kwargs):
        response = Response({'message':'User successfully logged out'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response 

#  Profile (Authenticated users only)
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the currently logged-in user
        return self.request.user
