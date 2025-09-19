from rest_framework import generics
from rest_framework.permissions import IsAuthenticated , AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer, UpdateProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .authentication import CookieJWTAuthentication
from drf_spectacular.utils import extend_schema

class DeleteAccountView(APIView):
    permission_classes =[IsAuthenticated]
    authentication_classes= [CookieJWTAuthentication]

    @extend_schema(
        tags=["User"],
        summary="Delete user account",
        description="Deletes the authenticated user’s account permanently."
    )

    def delete(self,request):
        user = self.request.user
        user.delete()
        response = Response({'message': 'User Profile Successfuly deleted'}, status= status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    
@extend_schema(
        tags=["User"],
        summary="Update user profile",
        description="Updates full_name , or password for the authenticated user."
    )
class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UpdateProfileSerializer
    permission_classes =[IsAuthenticated]
    authentication_classes=[CookieJWTAuthentication]

    def get_object(self):
        return self.request.user

class RefreshTokenView(APIView):
    @extend_schema(
        tags=["Authentication"],
        summary="Refresh token",
        description="Gets new access token with the existing refresh token."
    )
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
@extend_schema(
        tags=["Authentication"],
        summary="Register a new user",
        description="Creates a new user account with email, full name, and password."
    )
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    authentication_classes = []
    

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Login user",
        description="Logs in a user and sets access and refresh tokens"
    )

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
#     {
#   "email": "rita@example.com",
#   "password": "mypassword123"
# }

#Delete the access and refresh tokens from the cookies
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    @extend_schema(
        tags=["Authentication"],
        summary="Logout user",
        description="Logs out the authenticated user by clearing cookies."
    )
    def post(self,request,*args,**kwargs):
        response = Response({'message':f'{self.request.user} successfully logged out'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response 

#  Profile (Authenticated users only)
@extend_schema(
        tags=["User"],
        summary="Gets user profile",
        description="Gets the profile of the logged in user."
    )
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


    def get_object(self):
        # Return the currently logged-in user
        return self.request.user
