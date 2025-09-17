from rest_framework import generics, permissions
from .models import Account
from .serializers import AccountSerializer
from .utils import generate_account_number

class AccountCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class= AccountSerializer

    def perform_create(self, serializer):
        account_number = generate_account_number()
        serializer.save(user = self.request.user, account_number= account_number)

class AccountListView(generics.ListAPIView):
    permission_classes= [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
class AccountDetailView(generics.RetrieveAPIView):
    permission_classes= [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)