from rest_framework import generics, permissions
from .models import Account
from .serializers import AccountSerializer
from .utils import generate_account_number
from drf_spectacular.utils import extend_schema

@extend_schema(
        tags=["Account"],
        summary="Get or List User Account",
        description="Get methods gets list of all the accounts by the same user ,while Create method creates a new object."
    )
class AccountListCreateView(generics.ListCreateAPIView):
    """Handles listing all accounts for the logged-in user and creating a new one"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        # Only return accounts owned by the current user
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically generate account number + attach user
        account_number = generate_account_number()
        serializer.save(user=self.request.user, account_number=account_number)

@extend_schema(
        tags=["Account"],
        summary="Retrieve ,Update or Delete User Account",
        description="Depending on the method choice, the user Acount either gets retrieved, updated or deleted."
    )
class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Handles retrieving, updating, and deleting a single account"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        # Restrict detail view to the logged-in user's accounts
        return Account.objects.filter(user=self.request.user)
