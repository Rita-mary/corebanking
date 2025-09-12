from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# Serializer for registering a new user
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length = 8)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "password"]

    def create(self, validated_data):
        # Use create_user from the custom manager (handles password hashing)
        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            password=validated_data["password"],
        )
        return user


# Serializer for returning user details (e.g., in profile)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name"]


# Serializer for login with JWT, returning tokens + user info in response
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)  # gives {refresh, access}

        # Add extra info to the login response
        data["full_name"] = self.user.full_name
        data["email"] = self.user.email
        return data

class UpdateProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required= False, min_length = 8,)
    class Meta:
        model = User
        fields= ('full_name','password')
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, val in validated_data.items():
            setattr(instance,attr,val)

        if password:
            instance.set_password(password)
        instance.save()
        return instance
    